from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Transaction
from .serializers import TransactionSerializer
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

class TransactionViewSet(generics.ListCreateAPIView):
    """
    Endpoint para listar e criar transações.
    ViewSet para transações, permitindo transferências por CPF.
    Permite transferências por CPF.
    """

    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Retorna apenas transações onde o usuário é o remetente ou o destinatário.
        Usa select_related para otimizar queries ao banco.
        """

        return Transaction.objects.filter(
            sender=self.request.user
        ).select_related("sender", "receiver")

    def perform_create(self, serializer):
        """
        Modifica a criação para garantir que o sender seja o usuário autenticado.
        """
        serializer.save(sender=self.request.user)


class TransactionDetailView(APIView):
    """
    View para visualizar uma transação específica do usuário autenticado.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, transaction_id, *args, **kwargs):
        """
        Exibe uma transação específica do usuário autenticado.
        """
        transaction = get_object_or_404(Transaction, id=transaction_id)
        
        if transaction.sender != request.user and transaction.receiver != request.user:
            return Response({"detail": "Você não tem permissão para visualizar essa transação."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data)
