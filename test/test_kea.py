import unittest
import json
from cloudstack import Kea


class TestKea(unittest.TestCase):
    def setUp(self):

        ranges = {'77828509-4043-40bc-8756-7745c8ec7a99':
                      {'vms': [{'nic':
                                    [{'type': 'Shared',
                                      'traffictype': 'Guest',
                                      'id': '33f1542c-1da7-405f-b600-18356b329f48',
                                      'networkid': '4f6c99d1-991f-4c67-80ab-54f8cbccf60c',
                                      'secondaryip': [],
                                      'ipaddress': '192.168.0.100',
                                      'broadcasturi': 'vlan://untagged',
                                      'isdefault': True,
                                      'macaddress': '06:32:b2:00:04:79',
                                      'gateway': '192.168.0.1',
                                      'netmask': '255.255.255.0',
                                      'networkname': 'defaultGuestNetwork'}],
                                'id': '859eca81-1052-4bb5-a9e3-d685a550e1bd'}],
                       'podid': 'b16a92f4-9b18-4e24-857f-0d48f7dde298',
                       'ip6cidr': '2001:db8:200::/64',
                       'gateway': '192.168.0.1',
                       'networkid': '4f6c99d1-991f-4c67-80ab-54f8cbccf60c'}}

        mapping = {
                    '77828509-4043-40bc-8756-7745c8ec7a99': {
                                                "pool": "2001:db8:ff00::/40",
                                                "prefix-len": 60,
                                                "interface-id": "VLAN200"
                                              },
                    '1b8400f3-2eac-45b1-8f55-9d9ff162a1d8': {
                                                "pool": "2001:db8:aa00::/40",
                                                "prefix-len": 60,
                                                "interface-id": "VLAN300"
                                              },
                  }
        config = {
            "Dhcp6": {
                "renew-timer": 1000,
                "rebind-timer": 2000,
                "preferred-lifetime": 86400,
                "valid-lifetime": 172800,
                "lease-database": {
                    "type": "memfile",
                    "persist": False,
                    "name": "/var/lib/kea/leases6.csv"
                },
                "interfaces-config": {
                    "interfaces": ["eth0/2001:db8:100::1"]
                },
                "mac-sources": ["any"],
                "subnet6": [
                    {
                        "subnet": "2001:db8:200::/64",
                        "interface-id": "VLAN200",
                        "reservation-mode": "out-of-pool",
                        "reservations": [
                            {
                                "hw-address": "06:32:b2:00:04:79",
                                "prefixes": ["2001:db8:ff00::/60"]
                            },
                            {
                                "hw-address": "06:a5:de:00:04:47",
                                "prefixes": ["2001:db8:ff00:10::/60"]
                            },
                            {
                                "hw-address": "06:37:38:00:05:1c",
                                "prefixes": ["2001:db8:ff00:20::/60"]
                            },
                            {
                                "hw-address": "06:67:70:00:04:61",
                                "prefixes": ["2001:db8:ff00:30::/60"]
                            },
                            {
                                "hw-address": "06:39:ec:00:04:c1",
                                "prefixes": ["2001:db8:ff00:40::/60"]
                            }
                        ]
                    },
                    {
                        "subnet": "2001:db8:300::/64",
                        "interface-id": "VLAN300",
                        "reservation-mode": "out-of-pool",
                        "reservations": [
                            {
                                "hw-address": "06:85:3e:00:01:c2",
                                "prefixes": ["2001:db8:aa00::/60"]
                            }
                        ]
                    }
                ]
            }
        }

        self.kea = Kea(ranges=ranges, mapping=mapping, config=config)

    def test_get_mapping(self):
        mapping = self.kea.get_mapping('77828509-4043-40bc-8756-7745c8ec7a99')
        self.assertEqual(mapping['interface-id'], 'VLAN200')
        self.assertEqual(mapping['pool'], '2001:db8:ff00::/40')
        self.assertEqual(mapping['prefix-len'], 60)

    def test_get_subnet_config(self):
        subnet = self.kea.get_subnet_config('2001:db8:200::/64')
        self.assertEqual(subnet['reservations'][0]['hw-address'],
                         '06:32:b2:00:04:79')
        self.assertEqual(subnet['reservations'][0]['prefixes'][0],
                         '2001:db8:ff00::/60')

    def test_find_next_reservation(self):
        mapping = self.kea.get_mapping('77828509-4043-40bc-8756-7745c8ec7a99')
        subnet = self.kea.get_subnet_config('2001:db8:200::/64')
        reservations = self.kea.get_reservations(subnet['reservations'])
        prefix = self.kea.find_next_prefix(reservations, mapping['pool'],
                                           mapping['prefix-len'])
        self.assertEqual(prefix, '2001:db8:ff00:50::/60')

    def test_get_kea_config(self):
        keacfg = self.kea.get_kea_configuration()
        self.assertEqual(keacfg['Dhcp6']['subnet6'][0]['subnet'],
                         '2001:db8:200::/64')
        self.assertEqual(keacfg['Dhcp6']['subnet6'][0]['reservations'][0]['hw-address'],
                         '06:32:b2:00:04:79')
        self.assertEqual(keacfg['Dhcp6']['subnet6'][0]['reservations'][0]['prefixes'][0],
                         '2001:db8:ff00:50::/60')

if __name__ == '__main__':
    unittest.main()
