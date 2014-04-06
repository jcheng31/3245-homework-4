import subprocess


def print_cron():
    try:
        crontab = subprocess.check_output('crontab -l', shell=True)
        print crontab
    except Exception:
        pass
