# callback_plugins/20_changed_summary.py
#
# NOTE ON NAMING: Ansible executes callback plugins in alphanumeric order. 
# We use the '02_' prefix to force this plugin to execute AFTER the warning 
# summary ('01_'), guaranteeing the changed items list is the final output 
# printed above the command prompt.

import textwrap
from ansible.plugins.callback import CallbackBase
from ansible import constants as C

class CallbackModule(CallbackBase):
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'notification'
    CALLBACK_NAME = '20_changed_summary'

    def __init__(self):
        super().__init__()
        self.changed_tasks = {}

    def v2_runner_on_ok(self, result):
        if result.is_changed():
            task = result.task_name
            host = result._host.get_name()
            
            if task not in self.changed_tasks:
                self.changed_tasks[task] = set()
                
            self.changed_tasks[task].add(host)

    def v2_playbook_on_stats(self, stats):
        self._display.banner("CHANGED ITEMS SUMMARY")
        
        if not self.changed_tasks:
            self._display.display("  No changes made.", color=C.COLOR_OK)
            self._display.display("")
            return
            
        for task, hosts in self.changed_tasks.items():
            self._display.display(f"\n  TASK: {task}", color=C.COLOR_CHANGED)
            
            short_hosts = [h.split('.')[0] for h in sorted(hosts)]
            
            host_list = ", ".join(short_hosts)
            wrapped_hosts = textwrap.fill(
                f"Hosts ({len(hosts)}): {host_list}",
                width=100,
                initial_indent="    ",
                subsequent_indent="    "
            )
            
            # Applies C.COLOR_CHANGED (yellow) to the host list block
            self._display.display(wrapped_hosts, color=C.COLOR_CHANGED)
            
        self._display.display("")
