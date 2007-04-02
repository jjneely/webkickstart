import nahant

class Kickstart(nahant.Kickstart):

    def audit(self):
        # kill auditd with a big hammer unless anyone really wants to use it
        # The auditd deamon in RHEL 3 is called "audit" in RHEL 4 "auditd"
        # We override for RHEL 3
        audittable = self.getKeys('enable', 'audit')
        if len(audittable) > 1:
            raise errors.ParseError('Multiple audit keys found')
        elif len(audittable) == 1:
            retval = """
# make sure audit is on
chkconfig audit on

"""
        else:
            retval = """
# turn off audit and wax any logs
chkconfig audit off
rm -rf /var/log/audit
rm -rf /var/log/audit.d/*

"""
        return retval            

