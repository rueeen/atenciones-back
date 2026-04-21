from django.urls import path
from .views import (
    CaseAttachmentCreateView,
    CaseCloseView,
    CaseCommentCreateView,
    CaseCreateView,
    load_subcategories,
    CaseDetailView,
    CaseListView,
    CaseReassignView,
    CaseTakeView,
    CaseTransferView,
    CaseUpdateView,
    CategoryCreateView,
    CategoryListView,
    PendingAreaCasesListView,
    SubcategoryCreateView,
)


app_name = 'cases'

urlpatterns = [
    path('', CaseListView.as_view(), name='list'),
    path('<int:pk>/', CaseDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', CaseUpdateView.as_view(), name='update'),
    path('<int:pk>/transfer/', CaseTransferView.as_view(), name='transfer'),
    path('<int:pk>/take/', CaseTakeView.as_view(), name='take'),
    path('<int:pk>/reassign/', CaseReassignView.as_view(), name='reassign'),
    path('<int:pk>/comment/', CaseCommentCreateView.as_view(), name='comment'),
    path('<int:pk>/attachment/',
         CaseAttachmentCreateView.as_view(), name='attachment'),
    path('<int:pk>/close/', CaseCloseView.as_view(), name='close'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('categories/new/', CategoryCreateView.as_view(), name='category-create'),
    path('pendientes-area/', PendingAreaCasesListView.as_view(), name='pending-area'),
    path('subcategories/new/', SubcategoryCreateView.as_view(),
         name='subcategory-create'),
    path('nuevo/', CaseCreateView.as_view(), name='create'),
    path('ajax/subcategories/', load_subcategories,
         name='ajax_load_subcategories'),
]
