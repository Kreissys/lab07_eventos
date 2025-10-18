from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as auth_login
from django.db import models
from django.db.models import Count
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from .forms import EventoForm, RegistroEventoForm
from .models import Evento, RegistroEvento

# ---- LISTA / DETALLE / CRUD EVENTOS ----

class EventoListView(ListView):
    model = Evento
    template_name = "eventos/evento_list.html"
    context_object_name = "eventos"

class EventoDetailView(DetailView):
    model = Evento
    template_name = "eventos/evento_detail.html"
    context_object_name = "evento"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            ya_registrado = RegistroEvento.objects.filter(
                evento=self.object, usuario=self.request.user
            ).exists()
        else:
            ya_registrado = False
        ctx["ya_registrado"] = ya_registrado
        ctx["form_registro"] = RegistroEventoForm()
        ctx["registros"] = self.object.registros.select_related("usuario")
        return ctx

class SoloOrganizadorMixin(UserPassesTestMixin):
    def test_func(self):
        evento = self.get_object()
        return self.request.user.is_superuser or evento.organizador == self.request.user

class EventoCreateView(LoginRequiredMixin, CreateView):
    model = Evento
    form_class = EventoForm
    template_name = "eventos/evento_form.html"

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.organizador = self.request.user
        obj.save()
        messages.success(self.request, "Evento creado.")
        return HttpResponseRedirect(reverse("eventos:detalle", args=[obj.pk]))

class EventoUpdateView(LoginRequiredMixin, SoloOrganizadorMixin, UpdateView):
    model = Evento
    form_class = EventoForm
    template_name = "eventos/evento_form.html"

    def form_valid(self, form):
        messages.success(self.request, "Evento actualizado.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("eventos:detalle", args=[self.object.pk])

class EventoDeleteView(LoginRequiredMixin, SoloOrganizadorMixin, DeleteView):
    model = Evento
    template_name = "eventos/evento_confirm_delete.html"
    success_url = reverse_lazy("eventos:lista")

# ---- INSCRIPCIONES ----

@login_required
def registrarme(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    if RegistroEvento.objects.filter(evento=evento, usuario=request.user).exists():
        messages.info(request, "Ya estás inscrito en este evento.")
        return redirect("eventos:detalle", pk=pk)

    RegistroEvento.objects.create(evento=evento, usuario=request.user)
    messages.success(request, "Inscripción realizada.")
    return redirect("eventos:detalle", pk=pk)

@login_required
def cambiar_estado_registro(request, registro_id):
    reg = get_object_or_404(RegistroEvento, id=registro_id)
    if (not request.user.is_superuser) and (reg.evento.organizador != self.request.user):
        raise Http404("No autorizado")

    nuevo_estado = request.GET.get("estado", RegistroEvento.CONFIRMADO)
    if nuevo_estado not in dict(RegistroEvento.ESTADOS):
        messages.error(request, "Estado no válido.")
        return redirect("eventos:detalle", pk=reg.evento.pk)

    reg.estado = nuevo_estado
    reg.save()
    messages.success(request, f"Estado cambiado a {nuevo_estado}.")
    return redirect("eventos:detalle", pk=reg.evento.pk)

# ---- REPORTES ----

def usuarios_mas_activos(request):
    top = (User.objects
           .annotate(confirmados=Count("registros_evento", filter=(
               models.Q(registros_evento__estado=RegistroEvento.CONFIRMADO)
           )))
           .order_by("-confirmados")[:10])
    return render(request, "eventos/reportes_usuarios_activos.html", {"top": top})

def eventos_del_mes(request):
    hoy = timezone.now()
    inicio_mes = hoy.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    if hoy.month == 12:
        fin_mes = inicio_mes.replace(year=hoy.year+1, month=1)
    else:
        fin_mes = inicio_mes.replace(month=hoy.month+1)

    total = Evento.objects.filter(fecha_inicio__gte=inicio_mes, fecha_inicio__lt=fin_mes).count()
    eventos = Evento.objects.filter(fecha_inicio__gte=inicio_mes, fecha_inicio__lt=fin_mes)
    return render(request, "eventos/reportes_eventos_mes.html",
                  {"total": total, "eventos": eventos, "inicio": inicio_mes, "fin": fin_mes})

def inscritos_por_evento(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    cantidad = evento.registros.count()
    return render(request, "eventos/reportes_inscritos_evento.html", {"evento": evento, "cantidad": cantidad})

def eventos_organizados_por_usuario(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    cantidad = user.eventos_organizados.count()
    eventos = user.eventos_organizados.all()
    return render(request, "eventos/reportes_organizados_usuario.html",
                  {"usuario": user, "cantidad": cantidad, "eventos": eventos})

# ---- SIGNUP (registro de usuarios) ----

def signup(request):
    """
    Registro básico con UserCreationForm.
    Por defecto, tras registrarse lo envío al login.
    Si prefieres login automático, descomenta auth_login(...) y cambia el redirect.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # --- opción: login automático ---
            # auth_login(request, user)
            # return redirect('eventos:lista')
            messages.success(request, "Cuenta creada. Inicia sesión para continuar.")
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})
