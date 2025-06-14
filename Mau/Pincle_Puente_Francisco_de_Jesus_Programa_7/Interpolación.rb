require 'gtk3'  # Importa la biblioteca GTK+3 para crear interfaces gráficas en Ruby

# === FUNCIÓN PARA CALCULAR LA INTERPOLACIÓN DE LAGRANGE EN UN PUNTO X ===
def lagrange(x, points)
  points.each_with_index.reduce(0.0) do |total, ((xi, yi), i)|
    term = points.each_with_index.reduce(yi) do |prod, ((xj, _), j)|
      i == j ? prod : prod * (x - xj) / (xi - xj)
    end
    total + term
  end
end

# === FUNCIÓN PARA MOSTRAR EL PROCEDIMIENTO PASO A PASO DE LAGRANGE ===
def lagrange_steps(points)
  steps = "=== DESARROLLO PASO A PASO ===\n\n"

  points.each_with_index do |(xi, yi), i|
    numerators = []
    denominators = []
    explanation = "Paso #{i+1}: Calculamos el término L_#{i}(x):\n"

    points.each_with_index do |(xj, _), j|
      next if i == j
      numerators << "(x - #{xj})"
      denominators << "(#{xi} - #{xj})"
    end

    li_expr = numerators.join(" * ") + " / " + denominators.join(" * ")
    explanation += "L_#{i}(x) = #{li_expr}\n"
    explanation += "Multiplicamos por y_#{i} = #{yi}:\n"
    explanation += "Término completo: #{yi} * (#{li_expr})\n\n"
    steps += explanation
  end

  steps += "=== POLINOMIO FINAL ===\nP(x) = " + points.each_with_index.map do |(xi, yi), i|
    numerators = []
    denominators = []
    points.each_with_index do |(xj, _), j|
      next if i == j
      numerators << "(x - #{xj})"
      denominators << "(#{xi} - #{xj})"
    end
    "#{yi} * (#{numerators.join(" * ")} / #{denominators.join(" * ")})"
  end.join(" + ") + "\n\n"

  steps
end

# === CREACIÓN DE LA APLICACIÓN GTK ===
app = Gtk::Application.new("com.gamer.lagrange", :flags_none)

app.signal_connect("activate") do |application|
  window = Gtk::ApplicationWindow.new(application)
  window.set_title("Interpolación LAGRANGE")
  window.set_default_size(1400, 750)
  window.set_border_width(10)

  grid = Gtk::Box.new(:horizontal, 10)
  window.override_background_color(:normal, Gdk::RGBA::new(0.1, 0.1, 0.1, 1))

  # === PANEL IZQUIERDO ===
  left_panel = Gtk::Box.new(:vertical, 10)

  entry = Gtk::Entry.new
  entry.placeholder_text = "Ej: (1,2);(2,3);(4,1)"
  entry.override_background_color(:normal, Gdk::RGBA::new(0.2, 0.2, 0.2, 1))
  entry.override_color(:normal, Gdk::RGBA::new(0, 1, 0, 1))

  button = Gtk::Button.new(label: "Calcular y Graficar")
  button.override_background_color(:normal, Gdk::RGBA::new(0.3, 0.3, 0.3, 1))
  button.override_color(:normal, Gdk::RGBA::new(0, 0, 0, 1))

  drawing_area = Gtk::DrawingArea.new
  drawing_area.set_size_request(900, 600)

  error_label = Gtk::Label.new
  error_label.override_color(:normal, Gdk::RGBA::new(1, 0, 0, 1))

  left_panel.pack_start(Gtk::Label.new("💻 Puntos de entrada (x,y):").tap { |l| l.override_color(:normal, Gdk::RGBA::new(0, 1, 1, 1)) }, expand: false, fill: false, padding: 0)
  left_panel.pack_start(entry, expand: false, fill: false, padding: 0)
  left_panel.pack_start(button, expand: false, fill: false, padding: 0)
  left_panel.pack_start(error_label, expand: false, fill: false, padding: 0)
  left_panel.pack_start(drawing_area, expand: true, fill: true, padding: 0)

  # === PANEL DERECHO ===
  right_panel = Gtk::Box.new(:vertical, 10)
  scrolled_window = Gtk::ScrolledWindow.new
  scrolled_window.set_policy(:automatic, :automatic)

  text_view = Gtk::TextView.new
  text_view.editable = false
  text_view.override_background_color(:normal, Gdk::RGBA::new(0.15, 0.15, 0.15, 1))
  text_view.override_color(:normal, Gdk::RGBA::new(0, 1, 0, 1))
  text_view.set_wrap_mode(:word)

  scrolled_window.add(text_view)

  note_label = Gtk::Label.new("""\
📌 Nota:
• Escribe puntos como (x,y);(x2,y2);...
• No repitas valores de x.
• Ejemplo válido: (1,2);(3,5);(4,1)
• Estilo visual: Gamer Mode Activado
""")
  note_label.override_color(:normal, Gdk::RGBA::new(1, 1, 1, 1))

  right_panel.pack_start(scrolled_window, expand: true, fill: true, padding: 0)
  right_panel.pack_start(note_label, expand: false, fill: false, padding: 10)

  # === LÓGICA DEL BOTÓN ===
  button.signal_connect("clicked") do
    begin
      raw_input = entry.text.strip
      points = raw_input.split(';').map do |pair|
        match = pair.strip.match(/\(?\s*(-?\d+(?:\.\d+)?)\s*,\s*(-?\d+(?:\.\d+)?)\s*\)?/)
        raise "Formato inválido: '#{pair}'" unless match
        [match[1].to_f, match[2].to_f]
      end

      xs = points.map(&:first)
      raise "Valores de x repetidos" if xs.uniq.size != xs.size

      error_label.text = ""
      text_view.buffer.text = lagrange_steps(points)

      # Calculamos rango de X y Y
      xmin = xs.min
      xmax = xs.max

      ys_eval = (0..1000).map do |i|
        x = xmin + (xmax - xmin) * i / 1000.0
        lagrange(x, points)
      end.select { |y| y.finite? }

      if ys_eval.empty?
        ymin = points.map(&:last).min - 1
        ymax = points.map(&:last).max + 1
      else
        ymin = [points.map(&:last).min, ys_eval.min].min
        ymax = [points.map(&:last).max, ys_eval.max].max
      end

      xrange = xmax - xmin
      yrange = ymax - ymin
      xmin -= 0.1 * xrange
      xmax += 0.1 * xrange
      ymin -= 0.1 * yrange
      ymax += 0.1 * yrange

      drawing_area.signal_connect("draw") do |_, cr|
        width = drawing_area.allocated_width
        height = drawing_area.allocated_height

        cr.set_source_rgb(0, 0, 0)
        cr.paint

        map_x = ->(x) { (x - xmin) / (xmax - xmin) * width }
        map_y = ->(y) { height - (y - ymin) / (ymax - ymin) * height }

        # Ejes
        cr.set_source_rgb(0.7, 0.7, 0.7)
        cr.set_line_width(1)

        eje_x = (0.between?(ymin, ymax)) ? map_y.call(0) : height
        cr.move_to(0, eje_x)
        cr.line_to(width, eje_x)
        cr.stroke

        eje_y = (0.between?(xmin, xmax)) ? map_x.call(0) : 0
        cr.move_to(eje_y, 0)
        cr.line_to(eje_y, height)
        cr.stroke

        # Puntos
        cr.set_source_rgb(1, 0, 0)
        points.each do |px, py|
          cx = map_x.call(px)
          cy = map_y.call(py)
          cr.arc(cx, cy, 4, 0, 2 * Math::PI)
          cr.fill
        end

        # Curva
        cr.set_source_rgb(0, 1, 0)
        cr.set_line_width(2)

        prev = nil
        steps = 1000
        (0..steps).each do |i|
          x = xmin + (xmax - xmin) * i / steps.to_f
          y = lagrange(x, points)
          next unless y.finite?
          xp = map_x.call(x)
          yp = map_y.call(y)

          if prev
            cr.move_to(*prev)
            cr.line_to(xp, yp)
          end
          prev = [xp, yp]
        end
        cr.stroke
      end

      drawing_area.queue_draw

    rescue => e
      error_label.text = "❌ Error: #{e.message}"
    end
  end

  grid.pack_start(left_panel, expand: true, fill: true, padding: 0)
  grid.pack_start(right_panel, expand: true, fill: true, padding: 0)

  window.add(grid)
  window.show_all
end

app.run
