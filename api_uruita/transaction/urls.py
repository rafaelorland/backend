from django.urls import path

from transaction.views import TransactionListView,TransactionConfirmPaymentView, TransactionDetailView, TransactionCreateView

urlpatterns = [
    path('', TransactionListView.as_view(), name='transaction-list'),  # Listagem de transações
    path('create/', TransactionCreateView.as_view(), name='transaction-create'),  # Criação de transação
    path('<uuid:transaction_id>/', TransactionDetailView.as_view(), name='transaction-detail'),  # Detalhes de transação
    path('<uuid:transaction_id>/confirm/', TransactionConfirmPaymentView.as_view(), name='transaction-confirm-payment'),  # Confirmação de pagamento
]
