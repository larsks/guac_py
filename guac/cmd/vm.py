import guac.cmd.vm_create
import guac.cmd.vm_delete


def init_commands(vm):
    vm.command()(guac.cmd.vm_create.create)
    vm.command()(guac.cmd.vm_delete.delete)
