{% extends "layout.html" %}
{% block titulo %}Aplicación cerrada{% endblock %}
{% block contenido %}
<section class="panel exit-panel">
    <h3>Datos guardados correctamente</h3>
    <p>Se ha creado la copia de seguridad final: <strong>{{ copia }}</strong></p>
    <p>Ya puedes cerrar esta pestaña. La aplicación ha guardado copia final y el proceso de Python se cerrará por completo en unos segundos.</p>
</section>
{% endblock %}
