from rest_framework import serializers
from .models import Transaction
from users.models import CustomUser

class TransactionCPFSerializer(serializers.ModelSerializer):
    """
    Serializer para transações, permitindo transferência por CPF.
    """

    receiver_cpf = serializers.CharField(write_only = True)
    sender = serializers.PrimaryKeyRelatedField(read_only = True)
    receiver = serializers.PrimaryKeyRelatedField(read_only = True)
    amount = serializers.DecimalField(max_digits = 10, decimal_places=2)
    sender_balance_before = serializers.DecimalField(max_digits = 10, decimal_places=2, read_only = True)
    sender_balance_after = serializers.DecimalField(max_digits = 10, decimal_places=2, read_only = True)
    receiver_balance_before = serializers.DecimalField(max_digits = 10, decimal_places=2, read_only = True)
    receiver_balance_after = serializers.DecimalField(max_digits = 10, decimal_places=2, read_only = True)
    comment = serializers.CharField(required=False, allow_blank = True, allow_null = True)
    status = serializers.ChoiceField(choices=Transaction.StatusChoices.choices, default=Transaction.StatusChoices.PENDING)
    timestamp = serializers.DateTimeField(read_only = True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'sender', 'receiver',  'receiver_cpf', 'amount',
            'sender_balance_before', 'sender_balance_after',
            'receiver_balance_before', 'receiver_balance_after',
            'comment', 'status', 'timestamp'
        ]

    def validate(self, attrs):
        """
        Valida a transação antes de salvar.
        Garante que o valor seja positivo e que o remetente não seja o mesmo que o destinatário.
        """

        amount = attrs.get('amount')
        sender = self.context['request'].user
        receiver_cpf = attrs.get('receiver_cpf')

        try:
            receiver = CustomUser.objects.get(cpf=receiver_cpf)
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError({"receiver_cpf": "Usuário com este CPF não encontrado."})

        if amount <= 0:
            raise serializers.ValidationError({"amount": "O valor da transação deve ser positivo."})
        if sender == receiver:
            raise serializers.ValidationError({"sender": "Não é possível transferir para si mesmo."})
        if sender.balance < amount:
            raise serializers.ValidationError({"amount": "Saldo insuficiente para esta transação."})

        attrs['receiver'] = receiver
        return attrs
 
    def create(self, validated_data): 
        """
        Lógica de criação de transação, incluindo atualização de saldo.
        """

        sender = self.context['request'].user
        receiver = validated_data.pop('receiver') 
        amount = validated_data.get('amount')

        sender_balance_before = sender.balance
        receiver_balance_before = receiver.balance

        # Atualizar os saldos
        sender.balance -= amount 
        receiver.balance += amount
        sender.save()
        receiver.save()

        validated_data['sender'] = sender
        validated_data['receiver'] = receiver 
        validated_data['sender_balance_before'] = sender_balance_before
        validated_data['sender_balance_after'] = sender.balance 
        validated_data['receiver_balance_before'] = receiver_balance_before
        validated_data['receiver_balance_after'] = receiver.balance
        validated_data['status'] = Transaction.StatusChoices.COMPLETED

        return super().create(validated_data)
