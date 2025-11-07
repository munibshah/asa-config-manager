#!/usr/bin/env python3
"""
Quick SSH test script to verify ASA credentials with legacy SSH support
"""
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException
import paramiko

def test_ssh_connection(host, username, password, secret=None):
    """Test SSH connection with given credentials and legacy SSH support"""
    
    # Configure paramiko to allow legacy algorithms BEFORE creating connection
    import paramiko.transport
    
    # Add legacy algorithms to the supported lists (convert to lists first)
    paramiko.Transport._preferred_kex = list(paramiko.Transport._preferred_kex) + [
        'diffie-hellman-group1-sha1',
        'diffie-hellman-group14-sha1', 
        'diffie-hellman-group-exchange-sha1',
        'diffie-hellman-group-exchange-sha256',
    ]
    
    paramiko.Transport._preferred_ciphers = list(paramiko.Transport._preferred_ciphers) + [
        'aes128-cbc',
        'aes192-cbc', 
        'aes256-cbc',
        'des3-cbc',
    ]
    
    paramiko.Transport._preferred_macs = list(paramiko.Transport._preferred_macs) + [
        'hmac-sha1',
        'hmac-sha1-96',
        'hmac-md5',
        'hmac-md5-96',
    ]
    
    device = {
        'device_type': 'cisco_asa',
        'host': host,
        'username': username,
        'password': password,
        'port': 22,
        'conn_timeout': 20,
        'auth_timeout': 20,
    }
    
    if secret:
        device['secret'] = secret
    
    try:
        print(f"Testing connection to {host} with user: {username} (with legacy SSH support)")
        
        connection = ConnectHandler(**device)
        
        # Try to get hostname
        output = connection.send_command('show hostname')
        print(f"✅ SUCCESS! Connected to ASA")
        print(f"Hostname: {output.strip()}")
        
        # Try a simple show command to verify access
        try:
            version_output = connection.send_command('show version | include Version')
            print(f"Version: {version_output.strip()}")
        except:
            print("(Version check skipped)")
        
        connection.disconnect()
        return True
        
    except NetmikoAuthenticationException as e:
        print(f"❌ Authentication failed for {username}:{password}")
        return False
    except NetmikoTimeoutException as e:
        print(f"❌ Connection timeout to {host}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    host = "192.168.1.13"
    
    # Test the specific credentials provided
    print(f"Testing SSH connection to ASA at {host} with legacy SSH support...")
    print("=" * 60)
    
    # Test cisco/cisco first since that's what was specified
    if test_ssh_connection(host, "cisco", "cisco"):
        print(f"\n🎉 Working credentials found!")
        print(f"Username: 'cisco'")
        print(f"Password: 'cisco'")
    else:
        print("\n❌ cisco/cisco credentials didn't work.")
        print("Trying with enable password...")
        if test_ssh_connection(host, "cisco", "cisco", "cisco"):
            print(f"\n🎉 Working credentials found with enable password!")
            print(f"Username: 'cisco'")
            print(f"Password: 'cisco'")
            print(f"Enable: 'cisco'")
        else:
            print("Still not working. May need different credentials or SSH configuration.")