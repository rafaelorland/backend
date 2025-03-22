from django.urls import path

from transaction.views import TransactionDetailView, TransactionViewSet

urlpatterns = [
    path('', TransactionViewSet.as_view(), name='transaction-create'),
    path('<uuid:transaction_id>/', TransactionDetailView.as_view(), name='transaction-detail'),
]
