from django.db import models
from django.utils.translation import gettext_lazy as _
from model_utils.models import TimeStampedModel, SoftDeletableModel, SoftDeletableManager
from typing import Optional, Any
from django.db.models import Q
from account.models import User

# Create your models here.
class DialogsModel(TimeStampedModel):
    id = models.BigAutoField(primary_key=True, verbose_name=_("Id"))
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User1"),
                              related_name="+", db_index=True)
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User2"),
                              related_name="+", db_index=True)

    class Meta:
        unique_together = (('user1', 'user2'), ('user2', 'user1'))
        verbose_name = _("Dialog")
        verbose_name_plural = _("Dialogs")

    def __str__(self):
        return _("Dialog between ") + f"{self.user1_id}, {self.user2_id}"

    @staticmethod
    def dialog_exists(u1: User, u2: User) -> Optional[Any]:
        return DialogsModel.objects.filter(Q(user1=u1, user2=u2) | Q(user1=u2, user2=u1)).first()

    @staticmethod
    def create_if_not_exists(u1: User, u2: User):
        res = DialogsModel.dialog_exists(u1, u2)
        if not res:
            DialogsModel.objects.create(user1=u1, user2=u2)

    @staticmethod
    def get_dialogs_for_user(user: User):
        return DialogsModel.objects.filter(Q(user1=user) | Q(user2=user))
    
    def get_profile_info(self, user):
        """
        Retrieve the profile information of a user based on their user_type.
        """
        if user.user_type == 'client':
            profile = getattr(user, 'clientprofile', None)
            return {
                'type': 'client',
                'name': f"{profile.firstName} {profile.lastName}" if profile else None
            }
        elif user.user_type == 'crew':
            profile = getattr(user, 'crewprofile', None)
            return {
                'type': 'crew',
                'name': profile.name if profile else None
            }
        # Add other profiles as needed for vendor, internal, etc.
        return {
            'type': user.user_type,
            'name': None  # Default if profile not found
        }


class MessageModel(TimeStampedModel, SoftDeletableModel):
    id = models.BigAutoField(primary_key=True, verbose_name=_("Id"))
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Author"),
                               related_name='from_user', db_index=True)
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("Recipient"),
                                  related_name='to_user', db_index=True)
    text = models.TextField(verbose_name=_("Text"), blank=True)
    read = models.BooleanField(verbose_name=_("Read"), default=False)
    all_objects = models.Manager()

    @staticmethod
    def get_unread_count_for_dialog_with_user(sender, recipient):
        return MessageModel.objects.filter(sender_id=sender, recipient_id=recipient, read=False).count()

    @staticmethod
    def get_last_message_for_dialog(sender, recipient):
        return MessageModel.objects.filter(
            Q(sender_id=sender, recipient_id=recipient) | Q(sender_id=recipient, recipient_id=sender)) \
            .select_related('sender', 'recipient').first()

    def __str__(self):
        return str(self.pk)

    def save(self, *args, **kwargs):
        super(MessageModel, self).save(*args, **kwargs)
        DialogsModel.create_if_not_exists(self.sender, self.recipient)

    class Meta:
        ordering = ('-created',)
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")
        
    
class InboxGroup(models.Model):
    name = models.CharField(max_length=255)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inbox_admin_groups')
    members = models.ManyToManyField(User, related_name='inbox_groups')

    def __str__(self):
        return self.name

class InboxMessage(models.Model):
    group = models.ForeignKey(InboxGroup, on_delete=models.CASCADE, related_name='inbox_messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender}: {self.message[:50]}"