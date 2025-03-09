from rest_framework import serializers
from .models import Transaction
from users.models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serializer personalizado para o modelo CustomUser.
    """

    balance = serializers.DecimalField(max_digits=10, decimal_places=2)
    cpf = serializers.CharField(max_length=14)
    phone_numbe = serializers.CharField(max_length=15, required=False, allow_blank=True, allow_null=True)
    is_verified_email = serializers.BooleanField()
    verification_code = serializers.CharField(max_length=4, required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'balance', 'cpf', 'phone_numbe', 'is_verified_email', 'verification_code']


class TransactionSerializer(serializers.ModelSerializer):
    """
    Serializer para o modelo Transaction.
    """

    sender = CustomUserSerializer(read_only=True)
    receiver = CustomUserSerializer(read_only=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    sender_balance_before = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    sender_balance_after = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    receiver_balance_before = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    receiver_balance_after = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    comment = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    status = serializers.ChoiceField(choices=Transaction.StatusChoices.choices, default=Transaction.StatusChoices.PENDING)
    timestamp = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'sender', 'receiver', 'amount',
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
        sender = attrs.get('sender')
        receiver = attrs.get('receiver')

        if amount <= 0:
            raise serializers.ValidationError({"amount": "O valor da transação deve ser positivo."})
        if sender == receiver:
            raise serializers.ValidationError({"sender": "Não é possível transferir para si mesmo."})
        

    def create(self, validated_data):
        """
        Lógica personalizada de criação, se necessário, para a transação.
        """

        return super().create(validated_data)

    def update(self, instance, validated_data):
        """
        Lógica personalizada de atualização da transação, especialmente para o status e saldo.
        """
        
        if validated_data.get('status') == Transaction.StatusChoices.COMPLETED:
            instance.confirm_payment()
        
        return super().update(instance, validated_data)

