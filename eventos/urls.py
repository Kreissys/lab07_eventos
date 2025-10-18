from django.urls import path
from . import views

app_name = "eventos"

urlpatterns = [
    path('', views.EventoListView.as_view(), name='lista'),
    path('evento/nuevo/', views.EventoCreateView.as_view(), name='crear'),
    path('evento/<int:pk>/', views.EventoDetailView.as_view(), name='detalle'),
    path('evento/<int:pk>/editar/', views.EventoUpdateView.as_view(), name='editar'),
    path('evento/<int:pk>/eliminar/', views.EventoDeleteView.as_view(), name='eliminar'),

    path('evento/<int:pk>/registrarme/', views.registrarme, name='registrarme'),
    path('registro/<int:registro_id>/cambiar-estado/', views.cambiar_estado_registro, name='cambiar_estado'),

    path('reportes/usuarios-activos/', views.usuarios_mas_activos, name='usuarios_activos'),
    path('reportes/eventos-mes/', views.eventos_del_mes, name='eventos_mes'),
    path('reportes/inscritos/<int:pk>/', views.inscritos_por_evento, name='inscritos_por_evento'),
    path('reportes/organizados/<int:user_id>/', views.eventos_organizados_por_usuario, name='organizados_por_usuario'),
]
