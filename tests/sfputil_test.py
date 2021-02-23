import sys
import os
from unittest import mock

import pytest
from click.testing import CliRunner

test_path = os.path.dirname(os.path.abspath(__file__))
modules_path = os.path.dirname(test_path)
sys.path.insert(0, modules_path)

sys.modules['sonic_platform'] = mock.MagicMock()
import sfputil.main as sfputil


class TestSfputil(object):
    def test_format_dict_value_to_string(self):
        sorted_key_table = [
            'rx1power',
            'rx2power',
            'rx3power',
            'rx4power',
            'tx1bias',
            'tx1power',
            'tx2bias',
            'tx2power',
            'tx3bias',
            'tx3power',
            'tx4bias',
            'tx4power'
        ]

        dom_info_dict = {
            'temperature': '41.7539C',
            'voltage': '3.2577Volts',
            'rx1power': '-1.6622dBm',
            'rx2power': '-1.7901dBm',
            'rx3power': '-1.6973dBm',
            'rx4power': '-2.0915dBm',
            'tx1bias': '35.8400mA',
            'tx2bias': '37.5780mA',
            'tx3bias': '35.8400mA',
            'tx4bias': '35.8400mA',
            'tx1power': 'N/A',
            'tx2power': 'N/A',
            'tx3power': 'N/A',
            'tx4power': 'N/A'
        }

        expected_output = '''\
                RX1Power: -1.6622dBm
                RX2Power: -1.7901dBm
                RX3Power: -1.6973dBm
                RX4Power: -2.0915dBm
                TX1Bias: 35.8400mA
                TX2Bias: 37.5780mA
                TX3Bias: 35.8400mA
                TX4Bias: 35.8400mA
'''

        output = sfputil.format_dict_value_to_string(sorted_key_table,
                                                     dom_info_dict,
                                                     sfputil.QSFP_DOM_CHANNEL_MONITOR_MAP,
                                                     sfputil.DOM_VALUE_UNIT_MAP)
        assert output == expected_output

        # Change temperature and voltage to floats and ensure units get appended
        dom_info_dict['temperature'] = 41.7539
        dom_info_dict['voltage'] = 3.2577

        output = sfputil.format_dict_value_to_string(sorted_key_table,
                                                     dom_info_dict,
                                                     sfputil.QSFP_DOM_CHANNEL_MONITOR_MAP,
                                                     sfputil.DOM_VALUE_UNIT_MAP)
        assert output == expected_output

    def test_convert_sfp_info_to_output_string(self):
        sfp_info_dict = {
            'type': 'QSFP28 or later',
            'type_abbrv_name': 'QSFP28',
            'manufacturer': 'Mellanox',
            'model': 'MCP1600-C003',
            'hardware_rev': 'A2',
            'serial': 'MT1636VS10561',
            'vendor_oui': '00-02-c9',
            'vendor_date': '2016-07-18',
            'connector': 'No separable connector',
            'encoding': '64B66B',
            'ext_identifier': 'Power Class 1(1.5W max)',
            'ext_rateselect_compliance': 'QSFP+ Rate Select Version 1',
            'cable_type': 'Length Cable Assembly(m)',
            'cable_length': '3',
            'application_advertisement': 'N/A',
            'specification_compliance': "{'10/40G Ethernet Compliance Code': '40GBASE-CR4'}",
            'dom_capability': "{'Tx_power_support': 'no', 'Rx_power_support': 'no', 'Voltage_support': 'no', 'Temp_support': 'no'}",
            'nominal_bit_rate': '255'
        }

        expected_output = '''\
        Application Advertisement: N/A
        Connector: No separable connector
        Encoding: 64B66B
        Extended Identifier: Power Class 1(1.5W max)
        Extended RateSelect Compliance: QSFP+ Rate Select Version 1
        Identifier: QSFP28 or later
        Length Cable Assembly(m): 3
        Nominal Bit Rate(100Mbs): 255
        Specification compliance:
                10/40G Ethernet Compliance Code: 40GBASE-CR4
        Vendor Date Code(YYYY-MM-DD Lot): 2016-07-18
        Vendor Name: Mellanox
        Vendor OUI: 00-02-c9
        Vendor PN: MCP1600-C003
        Vendor Rev: A2
        Vendor SN: MT1636VS10561
'''
        output = sfputil.convert_sfp_info_to_output_string(sfp_info_dict)
        assert output == expected_output

    def test_convert_dom_to_output_string(self):
        sfp_type = 'QSFP28 or later'

        dom_info_dict = {
            'temperature': '41.7539C',
            'voltage': '3.2577Volts',
            'rx1power': '-1.6622dBm',
            'rx2power': '-1.7901dBm',
            'rx3power': '-1.6973dBm',
            'rx4power': '-2.0915dBm',
            'tx1bias': '35.8400mA',
            'tx2bias': '37.5780mA',
            'tx3bias': '35.8400mA',
            'tx4bias': '35.8400mA',
            'tx1power': 'N/A',
            'tx2power': 'N/A',
            'tx3power': 'N/A',
            'tx4power': 'N/A'
        }

        expected_output = '''\
        ChannelMonitorValues:
                RX1Power: -1.6622dBm
                RX2Power: -1.7901dBm
                RX3Power: -1.6973dBm
                RX4Power: -2.0915dBm
                TX1Bias: 35.8400mA
                TX2Bias: 37.5780mA
                TX3Bias: 35.8400mA
                TX4Bias: 35.8400mA
        ChannelThresholdValues:
        ModuleMonitorValues:
                Temperature: 41.7539C
                Vcc: 3.2577Volts
        ModuleThresholdValues:
'''

        output = sfputil.convert_dom_to_output_string(sfp_type, dom_info_dict)
        assert output == expected_output

        # TODO: Add tests for other SFP types

    def test_get_physical_port_name(self):
        output = sfputil.get_physical_port_name(0, 0, False)
        assert output == '0'

        output = sfputil.get_physical_port_name('Ethernet0', 0, False)
        assert output == 'Ethernet0'

        output = sfputil.get_physical_port_name('Ethernet0', 0, True)
        assert output == 'Ethernet0:0 (ganged)'

    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(sfputil.cli.commands['version'], [])
        assert result.output.rstrip() == 'sfputil version {}'.format(sfputil.VERSION)
