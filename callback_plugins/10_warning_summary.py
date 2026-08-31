# callback_plugins/10_warning_summary.py
#
# NOTE ON NAMING: Ansible executes callback plugins in alphanumeric order based 
# on the plugin name, ignoring the order in ansible.cfg. 
# We use the '01_' prefix so this warning summary runs first, ensuring the 
# 'changed_summary' always prints at the absolute bottom of the terminal output.

import textwrap
from ansible.plugins.callback import CallbackBase
from ansible import constants as C

class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'aggregate'
    CALLBACK_NAME = '10_warning_summary'
    CALLBACK_NEEDS_ENABLED = True

    def __init__(self):
        super().__init__()
        # Structure: { task_name: { (msg, color): set(hosts) } }
        self.task_warnings = {}

    def _add_warning(self, task, host, msg, color):
        short_host = host.split('.')[0] if host else 'global'
        if task not in self.task_warnings:
            self.task_warnings[task] = {}
        
        key = (msg, color)
        if key not in self.task_warnings[task]:
            self.task_warnings[task][key] = set()
            
        self.task_warnings[task][key].add(short_host)

    def _extract_warnings(self, result):
        host = result._host.get_name() if result._host else 'global'
        task = result._task.get_name() if result._task else 'Global / Internal'
        res_dict = getattr(result, '_result', {})

        for warn in res_dict.get('warnings', []):
            self._add_warning(task, host, f"[WARNING] {warn}", C.COLOR_WARN)

        for dep in res_dict.get('deprecations', []):
            msg = dep.get('msg', str(dep)) if isinstance(dep, dict) else str(dep)
            self._add_warning(task, host, f"[DEPRECATION] {msg}", C.COLOR_DEPRECATE)

    def v2_runner_on_ok(self, result):
        self._extract_warnings(result)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        self._extract_warnings(result)

    def v2_runner_on_warning(self, result, warning):
        host = result._host.get_name() if result._host else 'global'
        task = result._task.get_name() if result._task else 'Global / Internal'
        self._add_warning(task, host, f"[WARNING] {warning}", C.COLOR_WARN)

    def v2_runner_on_deprecation(self, result, deprecation):
        host = result._host.get_name() if result._host else 'global'
        task = result._task.get_name() if result._task else 'Global / Internal'
        msg = deprecation.get('msg', str(deprecation)) if isinstance(deprecation, dict) else str(deprecation)
        self._add_warning(task, host, f"[DEPRECATION] {msg}", C.COLOR_DEPRECATE)

    def v2_playbook_on_stats(self, stats):
        if not self.task_warnings:
            return

        self._display.banner("WARNINGS & DEPRECATIONS SUMMARY")
        
        for task, warnings in self.task_warnings.items():
            self._display.display(f"\n  TASK: {task}", color=C.COLOR_WARN)
            
            for (msg, color), hosts in warnings.items():
                self._display.display(f"    - {msg}", color=color)
                
                host_list = ", ".join(sorted(hosts))
                wrapped_hosts = textwrap.fill(
                    f"Hosts ({len(hosts)}): {host_list}",
                    width=100,
                    initial_indent="        ",
                    subsequent_indent="        "
                )
                self._display.display(wrapped_hosts)
                
        self._display.display("")
