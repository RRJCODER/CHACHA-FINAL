{% extends "layout.html" %}
{% block titulo %}Registro de jornada{% endblock %}

{% block contenido %}
<section class="panel highlight-panel">
    <div class="panel-head">
        <div>
            <h3>Nueva jornada</h3>
            <p class="subtext">Introduce manualmente las horas trabajadas y, en paralelo, las horas extra que quieres cuantificar para pago.</p>
        </div>
    </div>

    {% if trabajadores and obras %}
    <form method="post" class="form-grid form-grid-large" id="form-jornada">
        <div>
            <label>Fecha</label>
            <input type="date" name="fecha" value="{{ hoy }}" required>
        </div>

        <div>
            <label>Trabajador</label>
            <select name="trabajador_id" required>
                {% for t in trabajadores %}
                <option value="{{ t.id }}" data-precio-extra="{{ t.precio_hora }}">{{ t.nombre }} · {{ "%.2f"|format(t.precio_hora) }} €/h extra</option>
                {% endfor %}
            </select>
        </div>

        <div>
            <label>Obra</label>
            <select name="obra_id" required>
                {% for o in obras %}
                <option value="{{ o.id }}">{{ o.nombre }}</option>
                {% endfor %}
            </select>
        </div>

        <div>
            <label>Horas trabajadas</label>
            <input type="number" step="0.01" min="0" name="horas" placeholder="Ej. 10" required>
            <small>Control interno de jornada. No se paga desde la app.</small>
        </div>

        <div>
            <label>Horas extra</label>
            <input type="number" step="0.01" min="0" name="horas_extra" placeholder="Ej. 2" value="0" required>
            <small>Estas son las horas que se cuantifican para pagar.</small>
        </div>

        <div>
            <label>Dinero adelantado sobre extras</label>
            <input type="number" step="0.01" min="0" name="dinero_adelantado" value="0">
        </div>

        <div class="calc-card full">
            <div>
                <span>Horas trabajadas</span>
                <strong id="preview-horas">0.00</strong>
            </div>
            <div>
                <span>Horas extra a pagar</span>
                <strong id="preview-extra">0.00</strong>
            </div>
            <div>
                <span>Importe extra estimado</span>
                <strong id="preview-importe">0.00 €</strong>
            </div>
        </div>

        <div class="full">
            <label>Observaciones</label>
            <textarea name="observaciones" placeholder="Ej. Trabajadas 10 h, extras a pagar 2 h, material pendiente..."></textarea>
        </div>

        <button type="submit">Guardar jornada</button>
    </form>
    {% else %}
    <div class="notice">
        Primero debes crear al menos un trabajador y una obra.
    </div>
    {% endif %}
</section>

<section class="panel">
    <div class="panel-head">
        <h3>Historial de jornadas</h3>
    </div>

    <div class="table-wrap">
        <table>
            <thead>
                <tr>
                    <th>Fecha</th>
                    <th>Trabajador</th>
                    <th>Obra</th>
                    <th>Horas trabajadas</th>
                    <th>Horas extra</th>
                    <th>€/h extra</th>
                    <th>Importe extra</th>
                    <th>Adelanto</th>
                    <th>Pendiente</th>
                    <th>Estado</th>
                    <th>Observaciones</th>
                    <th></th>
                </tr>
            </thead>
            <tbody>
                {% for r in registros %}
                <tr>
                    <td>{{ r.fecha }}</td>
                    <td><strong>{{ r.trabajador }}</strong></td>
                    <td>{{ r.obra }}</td>
                    <td>{{ "%.2f"|format(r.horas) }}</td>
                    <td><strong>{{ "%.2f"|format(r.horas_extra) }}</strong></td>
                    <td>{{ "%.2f"|format(r.precio_hora) }} €</td>
                    <td>{{ "%.2f"|format(r.importe_extra) }} €</td>
                    <td>{{ "%.2f"|format(r.dinero_adelantado) }} €</td>
                    <td><strong>{{ "%.2f"|format(r.pendiente) }} €</strong></td>
                    <td>
                        {% if r.liquidado %}
                            <span class="badge paid">✓ Pagado</span>
                            <small>{{ r.fecha_liquidacion }}</small>
                        {% else %}
                            <span class="badge pending">Pendiente</span>
                        {% endif %}
                    </td>
                    <td>{{ r.observaciones }}</td>
                    <td class="actions">
                        {% if r.liquidado %}
                        <form method="post" action="{{ url_for('desliquidar_hora', id=r.id) }}" class="inline-form">
                            <button type="submit" class="link-button">Desmarcar pago</button>
                        </form>
                        {% else %}
                        <form method="post" action="{{ url_for('liquidar_hora', id=r.id) }}" class="inline-form">
                            <button type="submit" class="link-button">✓ Marcar pagado</button>
                        </form>
                        {% endif %}
                        <a class="danger" onclick="return confirm('¿Borrar este registro?')" href="{{ url_for('borrar_hora', id=r.id) }}">Borrar</a>
                    </td>
                </tr>
                {% else %}
                <tr><td colspan="12">No hay jornadas todavía.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</section>
{% endblock %}

{% block scripts %}
<script>
(function () {
    const form = document.getElementById('form-jornada');
    if (!form) return;
    const horas = form.querySelector('[name="horas"]');
    const extraInput = form.querySelector('[name="horas_extra"]');
    const trabajador = form.querySelector('[name="trabajador_id"]');
    const previewHoras = document.getElementById('preview-horas');
    const extra = document.getElementById('preview-extra');
    const importe = document.getElementById('preview-importe');

    function n(valor) {
        const parsed = parseFloat(String(valor || '0').replace(',', '.'));
        return Number.isFinite(parsed) ? parsed : 0;
    }

    function actualizar() {
        const total = Math.max(n(horas.value), 0);
        const hExtra = Math.max(n(extraInput.value), 0);
        const precio = n(trabajador.selectedOptions[0]?.dataset.precioExtra);
        previewHoras.textContent = total.toFixed(2);
        extra.textContent = hExtra.toFixed(2);
        importe.textContent = (hExtra * precio).toFixed(2) + ' €';
    }

    ['input', 'change'].forEach(evt => {
        horas.addEventListener(evt, actualizar);
        extraInput.addEventListener(evt, actualizar);
        trabajador.addEventListener(evt, actualizar);
    });
    actualizar();
})();
</script>
{% endblock %}
