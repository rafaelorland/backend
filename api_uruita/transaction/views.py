from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Transaction
from .serializers import TransactionSerializer
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

#Chat gpt
class TransactionCreateView(APIView):
    """
    View para criar uma nova transação. Apenas usuários autenticados podem criar transações.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Cria uma nova transação. O usuário logado será o remetente da transação.
        """
        # Garantir que o remetente da transação seja o usuário autenticado
        data = request.data.copy()
        data['sender'] = request.user.id  # O remetente será o usuário autenticado
        serializer = TransactionSerializer(data=data)

        if serializer.is_valid():
            try:
                # Salvar a transação
                transaction = serializer.save()

                # Se a transação for válida, retornamos os dados da transação criada
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            except ValidationError as e:
                # Retorna erro caso a transação não seja válida (ex. saldo insuficiente)
                return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # Retorna erro caso os dados da requisição não estejam corretos
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionListView(APIView):
    """
    View para listar as transações do usuário autenticado.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """
        Lista todas as transações do usuário autenticado.
        """
        # Filtra as transações para mostrar apenas as do usuário autenticado
        transactions = Transaction.objects.filter(sender=request.user) | Transaction.objects.filter(receiver=request.user)
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)


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
        
        # Verifica se a transação pertence ao usuário autenticado
        if transaction.sender != request.user and transaction.receiver != request.user:
            return Response({"detail": "Você não tem permissão para visualizar essa transação."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data)


class TransactionConfirmPaymentView(APIView):
    """
    View para confirmar o pagamento de uma transação. Apenas o remetente da transação pode confirmar o pagamento.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, transaction_id, *args, **kwargs):
        """
        Confirma o pagamento de uma transação. O usuário autenticado deve ser o remetente da transação.
        """
        transaction = get_object_or_404(Transaction, id=transaction_id)
        
        # Verifica se o usuário autenticado é o remetente da transação
        if transaction.sender != request.user:
            return Response({"detail": "Você não tem permissão para confirmar o pagamento desta transação."}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            transaction.confirm_payment()  # Chama a lógica para confirmar o pagamento
            serializer = TransactionSerializer(transaction)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except ValidationError as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
