import click
from natsort import natsorted
from tabulate import tabulate
from swsscommon.swsscommon import SonicV2Connector

import utilities_common.cli as clicommon
from sonic_py_common import multi_asic

CHASSIS_MODULE_INFO_TABLE = 'CHASSIS_MODULE_TABLE'
CHASSIS_MODULE_INFO_KEY_TEMPLATE = 'CHASSIS_MODULE {}'
CHASSIS_MODULE_INFO_DESC_FIELD = 'desc'
CHASSIS_MODULE_INFO_SLOT_FIELD = 'slot'
CHASSIS_MODULE_INFO_OPERSTATUS_FIELD = 'oper_status'
CHASSIS_MODULE_INFO_ADMINSTATUS_FIELD = 'admin_status'

CHASSIS_MIDPLANE_INFO_TABLE = 'CHASSIS_MIDPLANE_TABLE'
CHASSIS_MIDPLANE_INFO_IP_FIELD = 'ip_address'
CHASSIS_MIDPLANE_INFO_ACCESS_FIELD = 'access'

@click.group(cls=clicommon.AliasedGroup)
def chassis():
    """Chassis commands group"""
    pass

@chassis.group()
def modules():
    """Show chassis-modules information"""
    pass

@modules.command()
@clicommon.pass_db
@click.argument('chassis_module_name', metavar='<module_name>', required=False)
def status(db, chassis_module_name):
    """Show chassis-modules status"""

    header = ['Name', 'Description', 'Physical-Slot', 'Oper-Status', 'Admin-Status']
    chassis_cfg_table = db.cfgdb.get_table('CHASSIS_MODULE')

    state_db = SonicV2Connector(host="127.0.0.1")
    state_db.connect(state_db.STATE_DB)

    key_pattern = '*'
    if chassis_module_name:
        key_pattern = '|' + chassis_module_name

    keys = state_db.keys(state_db.STATE_DB, CHASSIS_MODULE_INFO_TABLE + key_pattern)
    if not keys:
        print('Key {} not found in {} table'.format(key_pattern, CHASSIS_MODULE_INFO_TABLE))
        return

    table = []
    for key in natsorted(keys):
        key_list = key.split('|')
        if len(key_list) != 2:  # error data in DB, log it and ignore
            print('Warn: Invalid Key {} in {} table'.format(key, CHASSIS_MODULE_INFO_TABLE))
            continue

        data_dict = state_db.get_all(state_db.STATE_DB, key)
        desc = data_dict[CHASSIS_MODULE_INFO_DESC_FIELD]
        slot = data_dict[CHASSIS_MODULE_INFO_SLOT_FIELD]
        oper_status = data_dict[CHASSIS_MODULE_INFO_OPERSTATUS_FIELD]

        admin_status = 'up'
        config_data = chassis_cfg_table.get(key_list[1])
        if config_data is not None:
            admin_status = config_data.get(CHASSIS_MODULE_INFO_ADMINSTATUS_FIELD)

        table.append((key_list[1], desc, slot, oper_status, admin_status))

    if table:
        click.echo(tabulate(table, header, tablefmt='simple', stralign='right'))
    else:
        click.echo('No data available in CHASSIS_MODULE_TABLE\n')

@modules.command()
@click.argument('chassis_module_name', metavar='<module_name>', required=False)
def midplane_status(chassis_module_name):
    """Show chassis-modules midplane-status"""

    header = ['Name', 'IP-Address', 'Reachability']

    state_db = SonicV2Connector(host="127.0.0.1")
    state_db.connect(state_db.STATE_DB)

    key_pattern = '*'
    if chassis_module_name:
        key_pattern = '|' + chassis_module_name

    keys = state_db.keys(state_db.STATE_DB, CHASSIS_MIDPLANE_INFO_TABLE + key_pattern)
    if not keys:
        print('Key {} not found in {} table'.format(key_pattern, CHASSIS_MIDPLANE_INFO_TABLE))
        return

    table = []
    for key in natsorted(keys):
        key_list = key.split('|')
        if len(key_list) != 2:  # error data in DB, log it and ignore
            print('Warn: Invalid Key {} in {} table'.format(key, CHASSIS_MIDPLANE_INFO_TABLE))
            continue

        data_dict = state_db.get_all(state_db.STATE_DB, key)
        ip = data_dict[CHASSIS_MIDPLANE_INFO_IP_FIELD]
        access = data_dict[CHASSIS_MIDPLANE_INFO_ACCESS_FIELD]

        table.append((key_list[1], ip, access))

    if table:
        click.echo(tabulate(table, header, tablefmt='simple', stralign='right'))
    else:
        click.echo('No data available in CHASSIS_MIDPLANE_TABLE\n')

@chassis.command()
@click.argument('systemportname', required=False)
@click.option('--namespace', '-n', 'namespace', required=True if multi_asic.is_multi_asic() else False, 
                default=None, type=str, show_default=False, help='Namespace name or all')
@click.option('--verbose', is_flag=True, help="Enable verbose output")
def system_ports(systemportname, namespace, verbose):
    """Show VOQ system ports information"""

    cmd = "voqutil -c system_ports"

    if systemportname is not None:
        cmd += " -i \"{}\"".format(systemportname)
    
    if namespace is not None:
        cmd += " -n {}".format(namespace)

    clicommon.run_command(cmd, display_cmd=verbose)

@chassis.command()
@click.argument('ipaddress', required=False)
@click.option('--asicname', '-x', 'asicname', default=None, type=str, show_default=False, help='Asic name')
@click.option('--verbose', is_flag=True, help="Enable verbose output")
def system_neighbors(asicname, ipaddress, verbose):
    """Show VOQ system neighbors information"""

    cmd = "voqutil -c system_neighbors"

    if ipaddress is not None:
        cmd += " -a {}".format(ipaddress)

    if asicname is not None:
        cmd += " -x {}".format(asicname)

    clicommon.run_command(cmd, display_cmd=verbose)

@chassis.command()
@click.argument('systemlagname', required=False)
@click.option('--asicname', '-x', 'asicname', default=None, type=str, show_default=False, help='Asic name')
@click.option('--verbose', is_flag=True, help="Enable verbose output")
def system_lags(systemlagname, asicname, verbose):
    """Show VOQ system lags information"""

    cmd = "voqutil -c system_lags"

    if systemlagname is not None:
        cmd += " -l \"{}\"".format(systemlagname)

    if asicname is not None:
        cmd += " -x {}".format(asicname)

    clicommon.run_command(cmd, display_cmd=verbose)
