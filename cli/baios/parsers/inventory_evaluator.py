#!/usr/bin/env python3
"""
bAIos inventory evaluator.

This module provides functionality to evaluate inventory items and check
if they are actually satisfied on the current system.
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import re
import json

from ..models.inventory import InventoryItem, InventorySection, InventoryReport, InventoryStatus


class InventoryEvaluator:
    """
    Evaluates inventory items against the current system to determine
    if requirements are met.
    """
    
    def __init__(self):
        """Initialize the evaluator."""
        self.evaluation_cache: Dict[str, Any] = {}
        self.system_info = self._collect_system_info()
    
    def _collect_system_info(self) -> Dict[str, Any]:
        """Collect basic system information for evaluations."""
        info = {
            'platform': os.name,
            'path_env': os.environ.get('PATH', '').split(os.pathsep),
            'home_dir': Path.home(),
            'user': os.environ.get('USER', os.environ.get('USERNAME', 'unknown')),
            'shell': os.environ.get('SHELL', ''),
            'wsl': 'microsoft' in os.environ.get('WSL_DISTRO_NAME', '').lower()
        }
        return info
    
    def evaluate_item(self, item: InventoryItem) -> InventoryItem:
        """
        Evaluate a single inventory item and update its status.
        
        Args:
            item: The inventory item to evaluate
            
        Returns:
            InventoryItem: Updated item with evaluated status
        """
        # Create a copy to avoid modifying the original
        evaluated_item = InventoryItem(
            id=item.id,
            description=item.description,
            section=item.section,
            category=item.category,
            status=item.status,
            details=item.details,
            check_command=item.check_command,
            install_command=item.install_command,
            dependencies=item.dependencies.copy(),
            metadata=item.metadata.copy()
        )
        
        # Perform the evaluation
        try:
            evaluation_result = self._perform_evaluation(evaluated_item)
            evaluated_item.status = evaluation_result['status']
            evaluated_item.details = evaluation_result['details']
            
            # Add evaluation metadata
            evaluated_item.metadata.update({
                'evaluated_at': evaluation_result.get('evaluated_at'),
                'evaluation_method': evaluation_result.get('method'),
                'check_output': evaluation_result.get('output', ''),
                'evaluation_success': evaluation_result['status'] == InventoryStatus.COMPLETE
            })
            
        except Exception as e:
            # If evaluation fails, mark as error
            evaluated_item.status = InventoryStatus.FAILED_NON_CRITICAL
            evaluated_item.details = f"Evaluation error: {str(e)}"
            evaluated_item.metadata['evaluation_error'] = str(e)
        
        return evaluated_item
    
    def _perform_evaluation(self, item: InventoryItem) -> Dict[str, Any]:
        """
        Perform the actual evaluation logic for an item.
        
        Args:
            item: The inventory item to evaluate
            
        Returns:
            Dict containing evaluation results
        """
        import datetime
        
        # Default result
        result = {
            'status': InventoryStatus.NOT_STARTED_REQUIRED,
            'details': 'Not evaluated',
            'method': 'none',
            'evaluated_at': datetime.datetime.now().isoformat()
        }
        
        # Strategy 1: Use the check command if available
        if item.check_command:
            return self._evaluate_with_command(item)
        
        # Strategy 2: Use category-specific evaluations
        category_evaluators = {
            'shell': self._evaluate_shell,
            'version_control': self._evaluate_version_control,
            'development_tools': self._evaluate_development_tools,
            'package_managers': self._evaluate_package_managers,
            'runtime': self._evaluate_runtime,
            'containerization': self._evaluate_containerization,
            'ai_tools': self._evaluate_ai_tools,
            'fonts': self._evaluate_fonts,
            'terminals': self._evaluate_terminals,
            'symlinks': self._evaluate_symlinks,
            'config': self._evaluate_config,
            'authentication': self._evaluate_authentication
        }
        
        if item.category in category_evaluators:
            return category_evaluators[item.category](item)
        
        # Strategy 3: Text-based pattern matching
        return self._evaluate_by_description(item)
    
    def _evaluate_with_command(self, item: InventoryItem) -> Dict[str, Any]:
        """Evaluate using the item's check command."""
        try:
            result = subprocess.run(
                item.check_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            success = result.returncode == 0
            output = result.stdout.strip() if result.stdout else result.stderr.strip()
            
            return {
                'status': InventoryStatus.COMPLETE if success else InventoryStatus.FAILED_NON_CRITICAL,
                'details': f"Check command result: {output}" if output else 
                          ("Check passed" if success else "Check failed"),
                'method': 'check_command',
                'output': output,
                'return_code': result.returncode,
                'evaluated_at': self._get_current_time()
            }
            
        except subprocess.TimeoutExpired:
            return {
                'status': InventoryStatus.FAILED_NON_CRITICAL,
                'details': 'Check command timed out',
                'method': 'check_command',
                'evaluated_at': self._get_current_time()
            }
        except Exception as e:
            return {
                'status': InventoryStatus.FAILED_NON_CRITICAL,
                'details': f'Command execution error: {str(e)}',
                'method': 'check_command',
                'evaluated_at': self._get_current_time()
            }
    
    def _evaluate_shell(self, item: InventoryItem) -> Dict[str, Any]:
        """Evaluate shell-related requirements."""
        description = item.description.lower()
        
        if 'zsh' in description:
            # Check if zsh is installed and is the default shell
            zsh_path = shutil.which('zsh')
            current_shell = self.system_info['shell']
            
            if zsh_path and 'zsh' in current_shell:
                return {
                    'status': InventoryStatus.COMPLETE,
                    'details': f'zsh installed at {zsh_path} and set as default shell',
                    'method': 'shell_check',
                    'evaluated_at': self._get_current_time()
                }
            elif zsh_path:
                return {
                    'status': InventoryStatus.FAILED_NON_CRITICAL,
                    'details': f'zsh installed at {zsh_path} but not set as default shell',
                    'method': 'shell_check',
                    'evaluated_at': self._get_current_time()
                }
            else:
                return {
                    'status': InventoryStatus.NOT_STARTED_REQUIRED,
                    'details': 'zsh not found in PATH',
                    'method': 'shell_check',
                    'evaluated_at': self._get_current_time()
                }
        
        if 'ohmyzsh' in description or 'oh-my-zsh' in description:
            oh_my_zsh_dir = self.system_info['home_dir'] / '.oh-my-zsh'
            if oh_my_zsh_dir.exists():
                return {
                    'status': InventoryStatus.COMPLETE,
                    'details': f'Oh My Zsh found at {oh_my_zsh_dir}',
                    'method': 'directory_check',
                    'evaluated_at': self._get_current_time()
                }
            else:
                return {
                    'status': InventoryStatus.NOT_STARTED_REQUIRED,
                    'details': 'Oh My Zsh directory not found',
                    'method': 'directory_check',
                    'evaluated_at': self._get_current_time()
                }
        
        return self._evaluate_generic(item)
    
    def _evaluate_version_control(self, item: InventoryItem) -> Dict[str, Any]:
        """Evaluate version control related requirements."""
        description = item.description.lower()
        
        if 'git' in description and 'github' not in description:
            git_path = shutil.which('git')
            if git_path:
                try:
                    result = subprocess.run(['git', '--version'], capture_output=True, text=True)
                    return {
                        'status': InventoryStatus.COMPLETE,
                        'details': f'Git found: {result.stdout.strip()}',
                        'method': 'command_check',
                        'evaluated_at': self._get_current_time()
                    }
                except:
                    pass
            
            return {
                'status': InventoryStatus.NOT_STARTED_REQUIRED,
                'details': 'Git not found or not working',
                'method': 'command_check',
                'evaluated_at': self._get_current_time()
            }
        
        if 'gh' in description and 'auth' in description:
            gh_path = shutil.which('gh')
            if gh_path:
                try:
                    result = subprocess.run(['gh', 'auth', 'status'], capture_output=True, text=True)
                    if result.returncode == 0:
                        return {
                            'status': InventoryStatus.COMPLETE,
                            'details': 'GitHub CLI authenticated',
                            'method': 'auth_check',
                            'evaluated_at': self._get_current_time()
                        }
                    else:
                        return {
                            'status': InventoryStatus.FAILED_NON_CRITICAL,
                            'details': 'GitHub CLI not authenticated',
                            'method': 'auth_check',
                            'evaluated_at': self._get_current_time()
                        }
                except:
                    pass
            
            return {
                'status': InventoryStatus.NOT_STARTED_REQUIRED,
                'details': 'GitHub CLI not found',
                'method': 'command_check',
                'evaluated_at': self._get_current_time()
            }
        
        if 'ssh' in description and 'key' in description:
            ssh_key_path = self.system_info['home_dir'] / '.ssh' / 'id_ed25519'
            if ssh_key_path.exists():
                return {
                    'status': InventoryStatus.COMPLETE,
                    'details': f'SSH key found at {ssh_key_path}',
                    'method': 'file_check',
                    'evaluated_at': self._get_current_time()
                }
            else:
                return {
                    'status': InventoryStatus.NOT_STARTED_REQUIRED,
                    'details': 'SSH key not found',
                    'method': 'file_check',
                    'evaluated_at': self._get_current_time()
                }
        
        return self._evaluate_generic(item)
    
    def _evaluate_development_tools(self, item: InventoryItem) -> Dict[str, Any]:
        """Evaluate development tools requirements."""
        description = item.description.lower()
        
        if 'neovim' in description or 'nvim' in description:
            nvim_path = shutil.which('nvim')
            if nvim_path:
                try:
                    result = subprocess.run(['nvim', '--version'], capture_output=True, text=True)
                    version_match = re.search(r'v(\d+\.\d+)', result.stdout)
                    if version_match:
                        version = float(version_match.group(1))
                        if version >= 0.11:
                            return {
                                'status': InventoryStatus.COMPLETE,
                                'details': f'Neovim v{version} found (>= 0.11 required)',
                                'method': 'version_check',
                                'evaluated_at': self._get_current_time()
                            }
                        else:
                            return {
                                'status': InventoryStatus.FAILED_NON_CRITICAL,
                                'details': f'Neovim v{version} found (< 0.11)',
                                'method': 'version_check',
                                'evaluated_at': self._get_current_time()
                            }
                except:
                    pass
            
            return {
                'status': InventoryStatus.NOT_STARTED_REQUIRED,
                'details': 'Neovim not found or version check failed',
                'method': 'command_check',
                'evaluated_at': self._get_current_time()
            }
        
        if 'lazyvim' in description:
            lazyvim_path = self.system_info['home_dir'] / '.config' / 'nvim'
            if lazyvim_path.exists():
                return {
                    'status': InventoryStatus.COMPLETE,
                    'details': f'Neovim config found at {lazyvim_path}',
                    'method': 'directory_check',
                    'evaluated_at': self._get_current_time()
                }
            else:
                return {
                    'status': InventoryStatus.NOT_STARTED_REQUIRED,
                    'details': 'Neovim config directory not found',
                    'method': 'directory_check',
                    'evaluated_at': self._get_current_time()
                }
        
        return self._evaluate_generic(item)
    
    def _evaluate_package_managers(self, item: InventoryItem) -> Dict[str, Any]:
        """Evaluate package managers."""
        return self._evaluate_tool_availability(item, ['mise', 'pipx', 'npm', 'pip'])
    
    def _evaluate_runtime(self, item: InventoryItem) -> Dict[str, Any]:
        """Evaluate runtime environments."""
        return self._evaluate_tool_availability(item, ['python', 'python3', 'node', 'nodejs', 'uv'])
    
    def _evaluate_containerization(self, item: InventoryItem) -> Dict[str, Any]:
        """Evaluate containerization tools."""
        description = item.description.lower()
        
        if 'docker' in description and 'hello' in description:
            # Try to run hello-world container
            docker_path = shutil.which('docker')
            if docker_path:
                try:
                    result = subprocess.run(
                        ['docker', 'run', '--rm', 'hello-world'], 
                        capture_output=True, 
                        text=True, 
                        timeout=60
                    )
                    if result.returncode == 0 and 'Hello from Docker' in result.stdout:
                        return {
                            'status': InventoryStatus.COMPLETE,
                            'details': 'Docker can run hello-world container',
                            'method': 'container_test',
                            'evaluated_at': self._get_current_time()
                        }
                    else:
                        return {
                            'status': InventoryStatus.FAILED_CRITICAL,
                            'details': 'Docker found but cannot run hello-world',
                            'method': 'container_test',
                            'evaluated_at': self._get_current_time()
                        }
                except subprocess.TimeoutExpired:
                    return {
                        'status': InventoryStatus.FAILED_NON_CRITICAL,
                        'details': 'Docker hello-world test timed out',
                        'method': 'container_test',
                        'evaluated_at': self._get_current_time()
                    }
                except Exception as e:
                    return {
                        'status': InventoryStatus.FAILED_CRITICAL,
                        'details': f'Docker test failed: {str(e)}',
                        'method': 'container_test',
                        'evaluated_at': self._get_current_time()
                    }
            
            return {
                'status': InventoryStatus.NOT_STARTED_REQUIRED,
                'details': 'Docker not found',
                'method': 'command_check',
                'evaluated_at': self._get_current_time()
            }
        
        return self._evaluate_tool_availability(item, ['docker', 'docker-compose'])
    
    def _evaluate_ai_tools(self, item: InventoryItem) -> Dict[str, Any]:
        """Evaluate AI tools."""
        return self._evaluate_tool_availability(item, ['gptme', 'claude', 'claude-flow'])
    
    def _evaluate_fonts(self, item: InventoryItem) -> Dict[str, Any]:
        """Evaluate font requirements."""
        # Fonts are difficult to check programmatically, so we'll mark as note
        return {
            'status': InventoryStatus.NOTE,
            'details': 'Font installation requires manual verification',
            'method': 'manual_check',
            'evaluated_at': self._get_current_time()
        }
    
    def _evaluate_terminals(self, item: InventoryItem) -> Dict[str, Any]:
        """Evaluate terminal applications."""
        # Terminal applications are system-specific, mark as note for now
        return {
            'status': InventoryStatus.NOTE,
            'details': 'Terminal installation requires manual verification',
            'method': 'manual_check',
            'evaluated_at': self._get_current_time()
        }
    
    def _evaluate_symlinks(self, item: InventoryItem) -> Dict[str, Any]:
        """Evaluate symlink requirements."""
        description = item.description.lower()
        
        symlink_checks = {
            'cursor': self.system_info['home_dir'] / '.local' / 'bin' / 'cursor',
            'vscode': self.system_info['home_dir'] / '.local' / 'bin' / 'code'
        }
        
        for tool, symlink_path in symlink_checks.items():
            if tool in description:
                if symlink_path.exists() and symlink_path.is_symlink():
                    return {
                        'status': InventoryStatus.COMPLETE,
                        'details': f'{tool} symlink found at {symlink_path}',
                        'method': 'symlink_check',
                        'evaluated_at': self._get_current_time()
                    }
                else:
                    return {
                        'status': InventoryStatus.NOT_STARTED_REQUIRED,
                        'details': f'{tool} symlink not found at {symlink_path}',
                        'method': 'symlink_check',
                        'evaluated_at': self._get_current_time()
                    }
        
        return self._evaluate_generic(item)
    
    def _evaluate_config(self, item: InventoryItem) -> Dict[str, Any]:
        """Evaluate configuration requirements."""
        description = item.description.lower()
        
        if 'zshrc' in description:
            zshrc_path = self.system_info['home_dir'] / '.zshrc'
            if zshrc_path.exists():
                # Check for specific content if mentioned in description
                try:
                    content = zshrc_path.read_text()
                    if 'export ZSH_CUSTOM' in description:
                        if 'export ZSH_CUSTOM=' in content:
                            return {
                                'status': InventoryStatus.COMPLETE,
                                'details': 'ZSH_CUSTOM export found in .zshrc',
                                'method': 'config_check',
                                'evaluated_at': self._get_current_time()
                            }
                        else:
                            return {
                                'status': InventoryStatus.FAILED_NON_CRITICAL,
                                'details': 'ZSH_CUSTOM export not found in .zshrc',
                                'method': 'config_check',
                                'evaluated_at': self._get_current_time()
                            }
                    else:
                        return {
                            'status': InventoryStatus.COMPLETE,
                            'details': '.zshrc file exists',
                            'method': 'file_check',
                            'evaluated_at': self._get_current_time()
                        }
                except Exception as e:
                    return {
                        'status': InventoryStatus.FAILED_NON_CRITICAL,
                        'details': f'.zshrc exists but cannot read: {str(e)}',
                        'method': 'file_check',
                        'evaluated_at': self._get_current_time()
                    }
            else:
                return {
                    'status': InventoryStatus.NOT_STARTED_REQUIRED,
                    'details': '.zshrc file not found',
                    'method': 'file_check',
                    'evaluated_at': self._get_current_time()
                }
        
        return self._evaluate_generic(item)
    
    def _evaluate_authentication(self, item: InventoryItem) -> Dict[str, Any]:
        """Evaluate authentication requirements."""
        description = item.description.lower()
        
        if 'claude-code' in description and 'auth' in description:
            # Check if claude-code is authenticated
            try:
                result = subprocess.run(['claude', 'auth', 'whoami'], capture_output=True, text=True)
                if result.returncode == 0:
                    return {
                        'status': InventoryStatus.COMPLETE,
                        'details': 'Claude Code is authenticated',
                        'method': 'auth_check',
                        'evaluated_at': self._get_current_time()
                    }
                else:
                    return {
                        'status': InventoryStatus.FAILED_NON_CRITICAL,
                        'details': 'Claude Code not authenticated',
                        'method': 'auth_check',
                        'evaluated_at': self._get_current_time()
                    }
            except Exception as e:
                return {
                    'status': InventoryStatus.NOT_STARTED_REQUIRED,
                    'details': f'Cannot check Claude Code auth: {str(e)}',
                    'method': 'auth_check',
                    'evaluated_at': self._get_current_time()
                }
        
        return self._evaluate_generic(item)
    
    def _evaluate_tool_availability(self, item: InventoryItem, tools: List[str]) -> Dict[str, Any]:
        """Generic tool availability check."""
        description = item.description.lower()
        
        for tool in tools:
            if tool in description:
                tool_path = shutil.which(tool)
                if tool_path:
                    try:
                        # Try to get version
                        result = subprocess.run([tool, '--version'], capture_output=True, text=True, timeout=10)
                        if result.returncode == 0:
                            version_info = result.stdout.strip().split('\n')[0]
                            return {
                                'status': InventoryStatus.COMPLETE,
                                'details': f'{tool} found: {version_info}',
                                'method': 'command_check',
                                'evaluated_at': self._get_current_time()
                            }
                    except:
                        pass
                    
                    return {
                        'status': InventoryStatus.COMPLETE,
                        'details': f'{tool} found at {tool_path}',
                        'method': 'command_check',
                        'evaluated_at': self._get_current_time()
                    }
                else:
                    return {
                        'status': InventoryStatus.NOT_STARTED_REQUIRED,
                        'details': f'{tool} not found in PATH',
                        'method': 'command_check',
                        'evaluated_at': self._get_current_time()
                    }
        
        return self._evaluate_generic(item)
    
    def _evaluate_by_description(self, item: InventoryItem) -> Dict[str, Any]:
        """Fallback evaluation based on description patterns."""
        description = item.description.lower()
        
        # Check for directory/file patterns
        path_patterns = re.findall(r'[`~]([/\w\.-]+)[`~]?', item.description)
        for path_str in path_patterns:
            path = Path(path_str.replace('~', str(self.system_info['home_dir'])))
            if path.exists():
                return {
                    'status': InventoryStatus.COMPLETE,
                    'details': f'Path exists: {path}',
                    'method': 'path_check',
                    'evaluated_at': self._get_current_time()
                }
        
        # Check for common installation keywords
        if any(keyword in description for keyword in ['install', 'download', 'clone', 'place']):
            return {
                'status': InventoryStatus.NOT_STARTED_REQUIRED,
                'details': 'Installation required (detected from description)',
                'method': 'keyword_analysis',
                'evaluated_at': self._get_current_time()
            }
        
        return self._evaluate_generic(item)
    
    def _evaluate_generic(self, item: InventoryItem) -> Dict[str, Any]:
        """Generic evaluation for items that don't match specific patterns."""
        return {
            'status': InventoryStatus.NOT_STARTED_REQUIRED,
            'details': 'Manual verification required',
            'method': 'generic',
            'evaluated_at': self._get_current_time()
        }
    
    def _get_current_time(self) -> str:
        """Get current timestamp."""
        import datetime
        return datetime.datetime.now().isoformat()
    
    def evaluate_section(self, section: InventorySection) -> InventorySection:
        """
        Evaluate all items in a section.
        
        Args:
            section: The inventory section to evaluate
            
        Returns:
            InventorySection: Section with all items evaluated
        """
        evaluated_section = InventorySection(
            name=section.name,
            description=section.description,
            metadata=section.metadata.copy()
        )
        
        for item in section.items:
            evaluated_item = self.evaluate_item(item)
            evaluated_section.add_item(evaluated_item)
        
        return evaluated_section
    
    def evaluate_report(self, report: InventoryReport) -> InventoryReport:
        """
        Evaluate all items in a complete report.
        
        Args:
            report: The inventory report to evaluate
            
        Returns:
            InventoryReport: Report with all items evaluated
        """
        evaluated_report = InventoryReport(
            env_keys=report.env_keys.copy(),
            metadata=report.metadata.copy(),
            generated_at=report.generated_at
        )
        
        # Add evaluation metadata
        evaluated_report.metadata.update({
            'evaluated_at': self._get_current_time(),
            'evaluator_version': '1.0.0',
            'system_info': self.system_info
        })
        
        for section in report.sections:
            evaluated_section = self.evaluate_section(section)
            evaluated_report.add_section(evaluated_section)
        
        return evaluated_report