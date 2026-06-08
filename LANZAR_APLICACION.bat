{% extends "layout.html" %}
{% block titulo %}Editar obra{% endblock %}

{% block contenido %}
<section class="panel narrow">
    <div class="panel-head">
        <h3>Editar obra</h3>
    </div>

    <form method="post" class="form-vertical">
        <label>Nombre de la obra</label>
        <input type="text" name="nombre" value="{{ obra.nombre }}" required>

        <label>Cliente</label>
        <input type="text" name="cliente" value="{{ obra.cliente }}">

        <label>Dirección</label>
        <input type="text" name="direccion" value="{{ obra.direccion }}">

        <button type="submit">Guardar cambios</button>
        <a class="cancel" href="{{ url_for('obras') }}">Cancelar</a>
    </form>
</section>
{% endblock %}