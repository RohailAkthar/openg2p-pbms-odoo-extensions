from odoo import models

class ResGroups(models.Model):
    _inherit = 'res.groups'

    def get_application_groups(self, domain=None):
        hidden_group_xml_ids = [
            'g2p_pbms_rule_access.group_eligibility_rule_viewer',
            'g2p_pbms_rule_access.group_eligibility_rule_editor',
            'g2p_pbms_rule_access.group_entitlement_rule_viewer',
            'g2p_pbms_rule_access.group_entitlement_rule_editor',
            'g2p_pbms_rule_access.group_enrolment_cycle_viewer',
            'g2p_pbms_rule_access.group_enrolment_cycle_editor',
            'g2p_pbms_rule_access.group_disbursement_cycle_viewer',
            'g2p_pbms_rule_access.group_disbursement_cycle_editor',
            'g2p_pbms_rule_access.group_entitlement_verif_config_viewer',
            'g2p_pbms_rule_access.group_entitlement_verif_config_editor',
            'g2p_pbms_rule_access.group_disbursement_verif_config_viewer',
            'g2p_pbms_rule_access.group_disbursement_verif_config_editor',
        ]
        hidden_group_ids = []
        for xml_id in hidden_group_xml_ids:
            group = self.env.ref(xml_id, raise_if_not_found=False)
            if group:
                hidden_group_ids.append(group.id)
        
        # Call super first to get the existing hidden groups from g2p_pbms
        # Then filter out our new groups too.
        # super() call should filter by the original domain and return the results.
        # If I want to add to the existing hidden list, I should modify the domain before calling super
        # OR I filter the output of super().
        
        res = super().get_application_groups(domain=domain)
        if hidden_group_ids:
           res = res.filtered(lambda g: g.id not in hidden_group_ids)
        return res
