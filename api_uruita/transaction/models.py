import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from users.models import CustomUser

class Transaction(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "PENDING", _("Pendente")
        COMPLETED = "COMPLETED", _("Concluída")
        FAILED = "FAILED", _("Falhou")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)
    sender = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="sent_transactions")
    receiver = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="received_transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    sender_balance_before = models.DecimalField(max_digits=10, decimal_places=2, editable=False, null=True, blank=True)
    sender_balance_after = models.DecimalField(max_digits=10, decimal_places=2, editable=False, null=True, blank=True)
    receiver_balance_before = models.DecimalField(max_digits=10, decimal_places=2, editable=False, null=True, blank=True)
    receiver_balance_after = models.DecimalField(max_digits=10, decimal_places=2, editable=False, null=True, blank=True)
    comment = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=10, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    timestamp = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.amount <= 0:
            raise ValidationError(_("O valor da transação deve ser positivo."))
        if self.sender == self.receiver:
            raise ValidationError(_("Não é possível transferir para si mesmo."))
        if self.status == self.StatusChoices.COMPLETED and self.sender.balance < self.amount:
            raise ValidationError(_("Saldo insuficiente para a transação."))

    def confirm_payment(self):
        if self.status != self.StatusChoices.PENDING:
            raise ValidationError(_("Apenas transações pendentes podem ser confirmadas."))

        if self.sender.balance < self.amount:
            self.status = self.StatusChoices.FAILED
            self.save(update_fields=["status"])
            raise ValidationError(_("Saldo insuficiente para completar a transação."))

        self.sender_balance_before = self.sender.balance
        self.receiver_balance_before = self.receiver.balance

        self.sender.balance -= self.amount
        self.receiver.balance += self.amount

        self.sender_balance_after = self.sender.balance
        self.receiver_balance_after = self.receiver.balance

        self.sender.save()
        self.receiver.save()

        self.status = self.StatusChoices.COMPLETED
        self.save(update_fields=["status", "sender_balance_before", "sender_balance_after", "receiver_balance_before", "receiver_balance_after"])

    def __str__(self):
        return f"{self.sender} → {self.receiver} | {self.amount} | {self.status}"
