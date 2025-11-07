#!/usr/bin/env python3
"""
Test common ASA default credentials
"""
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException
import paramiko

def configure_legacy_ssh():
    """Configure paramiko to support legacy SSH algorithms."""
    try:
        paramiko.Transport._preferred_kex = list(paramiko.Transport._preferred_kex) + [
            'diffie-hellman-group1-sha1',
            'diffie-hellman-group14-sha1', 
            'diffie-hellman-group-exchange-sha1',
        ]
        
        paramiko.Transport._preferred_ciphers = list(paramiko.Transport._preferred_ciphers) + [
            'aes128-cbc', 'aes256-cbc', 'des3-cbc',
        ]
        
        paramiko.Transport._preferred_macs = list(paramiko.Transport._preferred_macs) + [
            'hmac-sha1', 'hmac-md5',
        ]
    except:
        pass

def test_credentials(host, username, password, secret=None):
    """Test a specific credential combination."""
    configure_legacy_ssh()
    
    device = {
        'device_type': 'cisco_asa',
        'host': host,
        'username': username,
        'password': password,
        'port': 22,
        'conn_timeout': 15,
        'auth_timeout': 15,
    }
    
    if secret:
        device['secret'] = secret
    
    try:
        print(f"Testing: {username}/{password}" + (f" (enable: {secret})" if secret else ""))
        connection = ConnectHandler(**device)
        
        # Test basic command
        output = connection.send_command('show hostname', expect_string='')
        print(f"✅ SUCCESS! Hostname: {output.strip()}")
        
        connection.disconnect()
        return True
        
    except NetmikoAuthenticationException:
        print(f"❌ Auth failed")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)[:60]}...")
        return False

if __name__ == "__main__":
    host = "192.168.1.13"
    
    # Common ASA default credentials
    credentials = [
        # (username, password, enable_secret)
        ("cisco", "cisco", None),
        ("cisco", "cisco", "cisco"),
        ("admin", "admin", None),
        ("admin", "admin", "admin"),
        ("admin", "", None),
        ("admin", "", "admin"),
        ("", "", None),
        ("", "cisco", None),
        ("pix", "cisco", None),
        ("enable", "", None),
        ("admin", "password", None),
        ("admin", "cisco", None),
        ("asa", "asa", None),
    ]
    
    print(f"Testing common ASA credentials on {host}...")
    print("=" * 50)
    
    for username, password, secret in credentials:
        if test_credentials(host, username, password, secret):
            print(f"\n🎉 WORKING CREDENTIALS FOUND!")
            print(f"Username: '{username}'")
            print(f"Password: '{password}'")
            if secret:
                print(f"Enable: '{secret}'")
            break
        print()
    else:
        print("❌ No working credentials found from common defaults.")
        print("The ASA may have custom credentials configured.")