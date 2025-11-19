import subprocess

def change_rpi_ip(new_ip):
    try:
        ip_parts = new_ip.split('.')
        if len(ip_parts) != 4 or not all(p.isdigit() and 0 <= int(p) <= 255 for p in ip_parts):
            return False, "IP 형식 오류"

        router_ip = ".".join(ip_parts[:3]) + ".1"
        interface = "eth0"

        def run_cmd(args_list):
            print("[실행]", " ".join(args_list))
            result = subprocess.run(args_list, capture_output=True, text=True)
            print("[stdout]:", result.stdout.strip())
            print("[stderr]:", result.stderr.strip())
            if result.returncode != 0:
                raise subprocess.CalledProcessError(result.returncode, args_list, result.stdout, result.stderr)

        cp = "/usr/bin/cp"
        mv = "/bin/mv"
        restart_dhcpcd = "/bin/systemctl"

        run_cmd(['sudo', 'ip', 'addr', 'flush', 'dev', interface])
        run_cmd(['sudo', cp, '/etc/dhcpcd.conf', '/etc/dhcpcd.conf.bak'])

        with open("/etc/dhcpcd.conf", "r") as f:
            lines = f.readlines()

        cleaned = []
        skip = False
        for line in lines:
            if line.strip().startswith("interface eth0"):
                skip = True
            elif skip and line.strip() == "":
                skip = False
                continue
            if not skip:
                cleaned.append(line)

        new_block = [
            "\n# 웹에서 설정한 고정 IP\n",
            f"interface {interface}\n",
            "# Disable IPv6\n",
            "noipv6\n",
            f"static ip_address={new_ip}/24\n",
            f"static routers={router_ip}\n",
            f"static domain_name_servers={router_ip}\n"
        ]

        with open("/tmp/dhcpcd_new.conf", "w") as f:
            f.writelines(cleaned + new_block)

        run_cmd(['sudo', mv, '/tmp/dhcpcd_new.conf', '/etc/dhcpcd.conf'])

        run_cmd(['sudo', restart_dhcpcd, 'restart', 'dhcpcd'])

        return True, "IP 변경 및 dhcpcd 재시작 완료"

    except subprocess.CalledProcessError as e:
        return False, f"명령 오류: {e.stderr or str(e)}"
    except Exception as e:
        return False, f"예외 발생: {e}"


def get_current_ip(interface="eth0"):
    try:
        result = subprocess.run(
            ["ip", "-f", "inet", "addr", "show", interface],
            capture_output=True, text=True, check=True
        )
        for line in result.stdout.splitlines():
            line = line.strip()
            if line.startswith("inet "):
                ip = line.split()[1].split('/')[0]
                return ip
        return "IP 없음"
    except Exception as e:
        return f"에러: {e}"
