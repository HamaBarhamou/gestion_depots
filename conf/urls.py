"""
URL configuration for conf project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from comptes import views as comptes_views
from transactions import views as transactions_views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", comptes_views.tableau_de_bord, name="tableau_de_bord"),
    path("clients/", comptes_views.liste_clients, name="liste_clients"),
    path("clients/ajouter/", comptes_views.ajouter_client, name="ajouter_client"),
    path(
        "clients/<uuid:identifiant_unique>/",
        comptes_views.detail_client,
        name="detail_client",
    ),
    path(
        "transactions/enregistrer/",
        transactions_views.enregistrer_transaction,
        name="enregistrer_transaction",
    ),
    path(
        "bilan/journalier/",
        transactions_views.bilan_journalier,
        name="bilan_journalier",
    ),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(),
        name="logout",
    ),
    path("client-search/", comptes_views.client_search, name="client_search"),
]
