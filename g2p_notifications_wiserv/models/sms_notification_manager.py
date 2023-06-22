import logging

from zeep import Client

from odoo import _, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class NotificationManager(models.Model):
    _inherit = "g2p.program.notification.manager"

    def _selection_manager_ref_id(self):
        selection = super()._selection_manager_ref_id()
        new_manager = (
            "g2p.program.notification.manager.wiserv",
            "Wiserv SMS Notification",
        )
        if new_manager not in selection:
            selection.append(new_manager)
        return selection


class WiservNotificationManager(models.Model):
    _name = "g2p.program.notification.manager.wiserv"
    _description = "Wiserv Notification Manager"
    _inherit = [
        "g2p.program.notification.manager.sms",
        "mail.thread",
        "mail.activity.mixin",
    ]

    api_url = fields.Char("API URL", required=True)
    user_name = fields.Char(required=True)
    wiserv_password = fields.Char("Password", required=True)

    def send_sms_to_membership(self, membership, body):
        if (
            membership.partner_id.notification_preference in self.notification_types
            and membership.partner_id.phone
            and body
        ):
            if self.api_url and self.user_name and self.wiserv_password:
                try:
                    return self.send_sms(membership.partner_id.phone, body)
                except Exception as e:
                    # Handle general exception
                    _logger.exception("Error occurred during sendMessage:%s" % e)
                    error_msg = f"Error occurred during sendMessage to this partner: {membership.partner_id.name} ⟶ {e}"
                    self.message_post(
                        body=error_msg, subject=_("Wirserv Failure Response")
                    )
                    return None
            else:
                raise UserError(
                    _("Please configure Wiserv SMS configuration correctly.")
                )

    def send_sms(self, phone, body):
        if not (self.api_url and self.user_name and self.wiserv_password):
            raise UserError(_("Please configure Wiserv SMS configuration correctly."))

        client = Client(self.api_url)
        response = client.service.sendMessage(
            UserName=self.user_name,
            PassWord=self.wiserv_password,
            MobileNo=phone,
            Message=body,
        )
        _logger.debug("$$------------Response%s", response)
        return response
