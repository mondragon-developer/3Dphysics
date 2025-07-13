from vpython import *
#Web VPython 3.2
"""
Inclined Rail Physics 3D Simulation
===================================

This module creates an interactive 3D physics simulation that demonstrates the motion of a sphere
rolling down an inclined rail. The simulation incorporates multiple physics principles:
- Gravity and its components on an incline
- Friction forces
- Air resistance (drag)
- Buoyancy effects

The user interface allows for real-time adjustment of physical parameters including:
- Incline angle (0-90 degrees)
- Rail length (1-1000 meters)
- Gravitational acceleration (1-274 m/s²)
- Sphere mass (1-100 kg)
- Initial velocity (0-1000 m/s)

Calculations are performed using numerical integration with small time steps (dt)
to achieve accurate physical behavior.

Author: Jose Mondragon
"""

# Import core VPython modules for 3D rendering and UI widgets
from vpython import canvas, label, color, vector, box, sphere, rate, radians, sin, cos, button, wtext, slider, pi

# Placeholder for future graphing functionality
graph_plane = None

# ----------------- CANVAS SETUP ---------------------------------------------------------------------

# Create and configure the main 3D scene canvas
scene = canvas(
    container="vpython-container",  # HTML element ID where canvas will be embedded
    title='',                       # overwritten by custom HTML title below
    width=800, height=600,          # canvas size in pixels
    center=vector(0, 5, 0),         # center point of camera view
    background=color.white,         # white background (simulating air/vacuum)
    align='center'                  # center horizontally in page
)
# Position the camera for optimal viewing angle
scene.camera.pos  = vector(5, 5, 15)     # Camera position (x, y, z)
scene.camera.axis = vector(-5, -5, -15)  # Camera viewing direction

# CSS to center the canvas and style the page
css_style = """
<style>
  body {
    margin: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
    overflow-y: auto;
    background-color: #f0f0f0;
  }
  canvas { display: block; margin: 0 auto; }
</style>
"""
scene.append_to_caption(css_style)

# Add a custom HTML title block
scene.title = """
<div style="text-align:center; font-size:22px; font-weight:bold; margin-bottom:10px;">
  Inclined Rail Physics 3D Simulation<br>
  <span style="font-size:16px; font-weight:normal;">by Jose Mondragon</span>
</div>
"""

# Avatar setup (js has been minified)
def add_avatar_popup():
    popup_html = """<div style="text-align:center;margin:5px auto;padding:15px;background:linear-gradient(135deg,#ff6b35 0%,#f7931e 100%);color:white;border-radius:8px;width:800px;height:auto;display:flex;flex-direction:column;justify-content:center;align-items:center"><h4 style="margin:0 0 8px 0;font-size:16px">🤖 AI Physics Tutor</h4><p style="margin:0 0 12px 0;font-size:12px">Get help with physics concepts!</p><button onclick="openAvatarPopup()" style="padding:8px 20px;background:#1e3a8a;color:white;border:2px solid #1e40af;border-radius:5px;font-weight:bold;font-size:14px;cursor:pointer;transition:all 0.3s;box-shadow:0 2px 4px rgba(0,0,0,0.2);text-align:center;display:inline-block;vertical-align:middle" onmouseover="this.style.background='#1e40af';this.style.transform='translateY(-1px)'" onmouseout="this.style.background='#1e3a8a';this.style.transform='translateY(0)'">🚀 Launch Tutor</button><div id="popup-status" style="margin-top:8px;font-size:11px;opacity:0.9;text-align:center;width:100%"></div><p style="font-size:10px;margin:8px 0 0 0;opacity:0.8;text-align:center;width:100%">Voice interaction • Ask about simulation!</p></div><script>let a=null;function openAvatarPopup(){const b=event.target,s=document.getElementById('popup-status');a&&!a.closed&&a.close();b.innerHTML='Opening Avatar...';b.disabled=true;s.innerHTML='Opening avatar tutor window...';const f='width=500,height=300,left=100,top=100,scrollbars=yes,resizable=yes,toolbar=no,menubar=no,location=no,status=no';try{a=window.open('https://tinyurl.com/HeygenAvatarJMDragon','PhysicsAvatarTutor',f);if(a){const c=setInterval(()=>{a.closed&&(clearInterval(c),b.innerHTML='🚀 Launch Avatar Tutor',b.disabled=false,s.innerHTML='Avatar window closed. Click to reopen.')},1000);a.focus();s.innerHTML='✅ Avatar tutor opened! Switch to the popup window.';b.innerHTML='✅ Avatar Active';setTimeout(()=>{if(!a.closed){const d=document.createElement('button');d.innerHTML='❌ Close Avatar';d.style.cssText='margin-left:10px;padding:8px 16px;background:rgba(255,0,0,0.5);color:white;border:1px solid rgba(255,255,255,0.3);border-radius:5px;cursor:pointer';d.onclick=()=>{a&&!a.closed&&a.close()};b.parentNode.insertBefore(d,b.nextSibling)}},2000)}else throw new Error('Popup blocked')}catch(e){console.error('Popup error:',e);s.innerHTML='⚠️ Popup blocked ⚠️. Please allow popups for this site.';b.innerHTML='🚀 Launch Avatar Tutor 🚀';b.disabled=false;setTimeout(()=>{s.innerHTML+='<br><a href="https://tinyurl.com/HeygenAvatarJMDragon" target="_blank" style="color:white;text-decoration:underline">Click here to open in new tab instead</a>'},1000)}}window.addEventListener('beforeunload',()=>{a&&!a.closed&&a.close()})</script>"""
    try:
        scene.append_to_caption(popup_html)
    except Exception as e:
        print(f"Error appending popup HTML: {e}")
        scene.append_to_caption("<p>Failed to load the AI Tutor popup.</p>")
        
# ----------------- SIMULATION PARAMETERS ------------------------------------------------------------

# Core geometric and physical parameters
rail_length      = 10       # Length of the inclined rail (meters)
ball_radius      = 0.1      # Actual physical radius of sphere (meters) - used for physics calculations
show_radius      = 1      # Visual radius of sphere (meters) - scaled up for visibility
rail_width       = 0.4      # Visual thickness of the rail (meters)
g                = 9.81     # Earth's gravitational acceleration (m/s²)
t                = 0        # Simulation time tracker (seconds)
elapsed_time     = 0        # Time for UI display (seconds)
last_record_time = -0.1     # Last time data were recorded
speed            = 0        # Instantaneous speed of sphere along rail (m/s)
mass             = 1        # Mass of sphere (kg)
dt               = 0.0025   # Time step for numerical integration (seconds) - smaller steps = more accuracy
running          = False    # Flag to control simulation play/pause state
angle            = 30       # Initial incline angle (degrees)
initial_velocity = 0        # Initial launch speed along rail (m/s)
s                = 0        # Current displacement along the rail (meters)
drag_loss        = 0.0      # Total energy lost to air drag 
friction_loss    = 0.0      # total energy lost to friction (J)


# ----------------- ADVANCED PHYSICS PARAMETERS ------------------------------------------------------

# Air and material properties for realistic simulation
rho_air    = 1.225                                  # Air density at sea level (kg/m³)
Cd_sphere  = 0.47                                   # Drag coefficient for a sphere in air
area_cross = pi * ball_radius**2                    # Sphere cross-sectional area (m²) for drag calculation
mu_sa      = 0.2                                    # Coefficient of friction (steel on aluminum)
volume     = 4/3 * pi * ball_radius**3              # Sphere volume (m³) for buoyancy calculation
rho_sphere = mass / volume                          # Sphere density (kg/m³) for buoyancy effects

# Terminal velocity occurs when drag force equals gravity component:
# At 90° (free fall), terminal velocity = sqrt(2*m*g/(rho_air*Cd_sphere*area_cross))

# Data arrays for storing simulation results (tables or graphs)
times, heights, speeds, gravities = [], [], [], []

# Fixed endpoint of the rail in world coordinates (x, y, z)
fixed_point = vector(5, 0, 0)

def calculate_rail_geometry(angle):
    """
    Compute the rail's start point and incline angle based on the desired angle.
    
    This function uses trigonometry to determine the starting position of the rail
    given a fixed end point and the desired incline angle.
    
    Args:
        angle (float): The desired incline angle in degrees
        
    Returns:
        tuple: (rail_start: vector, angle_rad: float)
            - rail_start: 3D vector representing the starting position of the rail
            - angle_rad: The incline angle converted to radians for calculations
    """
    angle_rad = radians(angle)                      # Convert degrees to radians for trigonometric functions
    height    = rail_length * sin(angle_rad)            # Vertical rise of the rail
    base      = rail_length * cos(angle_rad)            # Horizontal run of the rail
    start_pt  = vector(fixed_point.x - base, height, 0) # Calculate start point based on geometry
    return start_pt, angle_rad

# Initialize rail geometry
rail_start, angle_rad = calculate_rail_geometry(angle)
rail_end = fixed_point                                  # The end point is fixed in the simulation

# ----------------- 3D OBJECTS CREATION ---------------------------------------------------------------

# Create the incline rail as a 3D box
rail = box(
    pos    = (rail_start + rail_end) / 2,  # Position at midpoint of rail length
    axis   = rail_end - rail_start,        # Direction and length vector
    length = rail_length,                  # Length matches our parameter
    height = 0.1,                          # Thickness of rail in vertical direction
    width  = rail_width,                   # Width of rail (into the screen)
    color  = vector(0.2, 0.4, 0.8)         # Blue color (RGB values)
)

# Create the rolling sphere with a trailing path to show its motion
ball = sphere(
    pos        = rail_start + vector(0, show_radius, 0),  # Start at rail beginning, elevated by radius
    radius     = show_radius,                             # Visual size of ball
    color      = vector(0.8, 0.2, 0.2),                   # Red color (RGB values)
    make_trail = True,                                    # Enable motion trail
    trail_type = "points",                                # Trail made of disconnected points
    interval   = 10,                                      # Draw a point every 10 time steps
    trail_color= vector(0.8, 0.2, 0.2)                    # Trail color matches ball
)

# Create a floor plane under the rail for visual reference
floor = box(
    pos    = vector(0, -0.05, 0),  # Just below the origin
    length = 20,                    # Length in x direction 
    height = 0.1,                   # Thin height
    width  = 4,                     # Width in z direction
    color  = vector(0.2, 0.6, 0.3)  # Green color (RGB values)
)

# ----------------- UI LABELS ----------------------------------------------------------------------------

# Create on-screen labels to display simulation data
time_label   = label(screen=True, text="Time: 0.00 s", xoffset=0,   yoffset=-60, box=False, line=False)
speed_label  = label(screen=True, text="Speed: 0.00 m/s", xoffset=0, yoffset=-80, box=False, line=False)
angle_label  = label(pos=rail_start + vector(0, -2, 0), text=f'Angle: {angle}°', height=16, color=color.black, box=False)
length_label = label(pos=fixed_point + vector(0, 2, 0), text=f'Length: {rail_length} m', height=16, color=color.black, box=False)
                     
energy_label = label(screen=True, text="", xoffset=0, yoffset=-100, box=False, line=False)
energy_label.text = f"Fg: 0.00 N   Fric: 0.00 N   Drag: 0.00 N   a: 0.00 m/s² \nPE: 0.00J   KE: 0.00 J  Fric Loss: 0.00J  Drag Loss: 0.00 J\n  TE: 0.00 J\nH. Speed: 0.00 m/s   V. Speed: 0.00 m/s"


# Placeholders for slider-value displays (current values)
angle_value, length_value, gravity_value = wtext(text=''), wtext(text=''), wtext(text='')

# ----------------- SIMULATION CONTROL FUNCTIONS ----------------------------------------------------------

def update_simulation():
    """
    Reconfigure the simulation when parameters change.
    
    This function updates the rail geometry and resets the ball position
    when the user changes parameters like angle or rail length.
    It also updates the associated labels and visual elements.
    """
    global rail_start, angle_rad
    # Recalculate rail geometry based on current angle
    rail_start, angle_rad = calculate_rail_geometry(angle)
    
    # Update rail position and orientation
    rail.pos  = (rail_start + rail_end) / 2
    rail.axis = rail_end - rail_start
    
    # Hide rail when angle is 90° (vertical drop)
    rail.visible = (angle != 90)
    
    # Update UI labels
    angle_label.text  = f'Angle: {angle}°'
    angle_label.pos   = rail_start + vector(0, 1, 0)
    length_label.text = f'Length: {rail_length} m'
    
    # Reset ball to start of rail
    ball.pos = rail_start + vector(0, show_radius, 0)
    ball.clear_trail()

def update_angle(slider):
    """
    Update the simulation angle when the angle slider changes.
    
    Args:
        slider: The slider UI element that triggered this callback
    """
    global angle
    angle = slider.value  # Get value from the slider
    angle_value.text = f'{angle}°<br>'  # Update text display
    update_simulation()  # Reconfigure the simulation with new angle

def update_length(slider):
    """
    Update the rail length when the length slider changes.
    
    Args:
        slider: The slider UI element that triggered this callback
    """
    global rail_length
    rail_length = slider.value  # Get value from the slider
    length_value.text = f'{rail_length} m<br>'  # Update text display
    update_simulation()  # Reconfigure the simulation with new length

def update_gravity(slider):
    """
    Update the gravitational acceleration when the gravity slider changes.
    
    Args:
        slider: The slider UI element that triggered this callback
    """
    global g
    g = slider.value  # Get value from the slider
    gravity_value.text = f'{g:.1f} m/s²<br>'  # Update text display

def update_mass(slider):
    """
    Update the ball mass when the mass slider changes.
    
    Args:
        slider: The slider UI element that triggered this callback
    """
    global mass
    mass = slider.value  # Get value from the slider
    mass_value.text = f'{mass}Kg<br>'
    update_simulation()

def update_initial_velocity(slider):
    """
    Update the initial velocity when the initial velocity slider changes.
    
    Args:
        slider: The slider UI element that triggered this callback
    """
    global initial_velocity, speed
    initial_velocity = slider.value  # Get value from the slider
    speed = initial_velocity
    initial_velocity_value.text = f'{initial_velocity}m/s<br>'
    update_simulation()

def reset_simulation():
    """
    Reset the simulation to its initial state.
    
    This function resets all time-dependent variables, clears data arrays,
    repositions the ball at the start, updates the UI elements, and pauses
    the simulation.
    """
    global t, elapsed_time, times, s, speed, heights, speeds, gravities, running
    global Fg_par, F_fric, F_drag, acceleration, drag_loss, friction_loss
    global forces_g, forces_f, forces_d, accelerations, energies_pe, energies_ke, energies_te
    global friction_losses, drag_losses, h_speeds, v_speeds, last_record_time
    # Reset time and motion variables
    t = 0
    s = 0
    elapsed_time = 0
    speed = initial_velocity
    drag_loss = 0.0
    friction_loss = 0.0
    F_drag = 0.
    last_record_time = -0.1
    
    
    # Initialize force variables
    Fg_par = 0          # Parallel component of gravity
    F_fric = 0          # Friction force
    F_drag = 0          # Air drag force
    acceleration = 0    # Net acceleration
    
    # Clear all data arrays
    times.clear(); heights.clear(); speeds.clear(); gravities.clear()
    forces_g.clear(); forces_f.clear(); forces_d.clear(); accelerations.clear()
    energies_pe.clear(); energies_ke.clear(); energies_te.clear()
    friction_losses.clear(); drag_losses.clear()
    h_speeds.clear(); v_speeds.clear()
    
    
    # Reset ball position and trail
    ball.pos = rail_start + vector(0, show_radius, 0)
    ball.clear_trail()
    
    # Update UI elements
    time_label.text  = f"Time: {elapsed_time:.2f} s"
    speed_label.text = f"Speed: {speed:.2f} m/s"
    energy_label.text = f"Fg∥: 0.00 N   Fric: 0.00 N   Drag: 0.00 N   a: 0.00 m/s² \nPE: 0.00J   KE: 0.00 J  Fric Loss: 0.00J  Drag Loss: 0.00 J\n  TE: 0.00 J\nH. Speed: 0.00 m/s   V. Speed: 0.00 m/s"
    data_count_label.text = "Data points: 0"
    

def toggle_running():
    """
    Toggle the simulation between running and paused states.
    
    This function is called when the Play/Pause button is pressed.
    It updates the button appearance and switches the simulation state.
    """
    global running
    running = not running  # Toggle the running flag
    
    # Update button appearance based on new state
    if running:
        play_button.color = color.red
        play_button.text  = "Pause"
    else:
        play_button.color = color.blue
        play_button.text  = "Play"

# ----------------- UI CONTROLS CREATION ----------------------------------------------------------------

# Create sliders with labels for adjusting simulation parameters
scene.append_to_caption("<b>Angle (°):</b>")
angle_slider = slider(min=0, max=90, step=1, value=angle, length=650, bind=update_angle)
angle_value  = wtext(text=f" {angle}°<br><br>")

scene.append_to_caption("<b>Rail Length (m):</b>")
length_slider = slider(min=1, max=1000, step=1, value=rail_length, length=600, bind=update_length)
length_value  = wtext(text=f" {rail_length} m<br><br>")

scene.append_to_caption("<b>Gravity (m/s²):</b>")
gravity_slider = slider(min=1, max=274, step=0.1, value=g, length=605, bind=update_gravity)
gravity_value  = wtext(text=f" {g:.1f} m/s²<br><br>")

scene.append_to_caption("<b>Mass (kg):</b>")
mass_slider = slider(min=1, max=100, step=1, value=mass, length=645, bind=update_mass)
mass_value = wtext(text=f" {mass:.1f}kg<br><br>")

scene.append_to_caption("<b>Initial Velocity (m/s):</b>")
initial_velocity_slider = slider(min=0, max=1000, step=1, value=initial_velocity, length=560, bind=update_initial_velocity)
initial_velocity_value = wtext(text=f"{initial_velocity:0.2f}m/s")

# Play/Pause and Reset buttons
play_button  = button(text="Play",  bind=toggle_running, color=color.green, pos=scene.title_anchor)
reset_button = button(text="Reset", bind=reset_simulation, color=color.red,   pos=scene.title_anchor)


# ----------------- DATA TABLE FUNCTIONALITY ------------------------------------------------------------

# Data arrays to track variables
forces_g, forces_f, forces_d = [], [], []               # Forces (gravity parallel, friction, drag)
accelerations = []                                      # Acceleration values
energies_pe, energies_ke, energies_te = [], [], []      # Energy values
friction_losses, drag_losses = [], []                   # Energy losses
h_speeds, v_speeds = [], []                             # Velocity components

# Variable to track if table is visible
table_visible = False
table_div_id = "data_table_container"

# Add data table button
scene.append_to_caption("<div style='text-align:center; margin:10px 0;'>")
data_table_button = button(text="Show Data Table", bind=toggle_data_table, color=color.blue)
scene.append_to_caption("</div>")

# Add data count indicator
data_count_label = label(screen=True, text="Data points: 0", xoffset=0, yoffset=-250, 
                         box=False, line=False, height=16, color=color.black)

# Add a container for the data table
scene.append_to_caption(f"""
<div id="{table_div_id}" style="display:none; position:fixed; top:50%; left:50%; 
     transform:translate(-50%, -50%); width:80%; height:80%; background-color:white; 
     z-index:1000; border:2px solid #333; box-shadow:0 0 15px rgba(0,0,0,0.2); 
     overflow:auto; padding:15px;">
    <div style="position:sticky; top:0; background-color:white; padding:10px; 
         display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #ddd;">
        <h2 style="margin:0;">Simulation Data Table</h2>
        <button id="close_table_button" style="padding:5px 10px; background-color:#f44336; 
                color:white; border:none; cursor:pointer;">Close</button>
    </div>
    <div id="table_content" style="margin-top:10px;">
        <!-- Table will be inserted here -->
    </div>
</div>
""")

def toggle_data_table():
    """
    Toggle the visibility of the data table and update its content.
    """
    global table_visible
    table_visible = not table_visible
    
    # Use JavaScript to toggle visibility and update content
    display_style = "block" if table_visible else "none"
    
    if table_visible:
        # Generate the table HTML
        table_html = generate_table_html()
        
        # Update the table content and display it
        js_code = f"""
        document.getElementById('{table_div_id}').style.display = '{display_style}';
        document.getElementById('table_content').innerHTML = `{table_html}`;
        document.getElementById('close_table_button').onclick = function() {{
            document.getElementById('{table_div_id}').style.display = 'none';
        }};
        """
    else:
        # Just hide the table
        js_code = f"""
        document.getElementById('{table_div_id}').style.display = '{display_style}';
        """
    
    # Execute the JavaScript
    scene.append_to_caption(f"<script>{js_code}</script>")
    
    # Toggle button text
    if table_visible:
        data_table_button.text = "Hide Data Table"
    else:
        data_table_button.text = "Show Data Table"

def generate_table_html():
    """
    Generate HTML for the data table.
    """
    # Create the table with CSS
    table_html = """
    <style>
    .data-table {
        border-collapse: collapse;
        width: 100%;
        font-family: Arial, sans-serif;
        font-size: 14px;
    }
    .data-table th, .data-table td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: center;
    }
    .data-table th {
        background-color: #4CAF50;
        color: white;
        position: sticky;
        top: 50px;
    }
    .data-table tr:nth-child(even) {
        background-color: #f2f2f2;
    }
    </style>
    
    <div style="margin:10px 0;">
        <strong>Parameters:</strong> Angle: """ + str(angle) + "° | Rail Length: " + str(rail_length) + "m | Mass: " + str(mass) + "kg | Gravity: " + f"{g:.2f}" + "m/s² | Friction Coef: " + str(mu_sa) + """
    </div>
    
    <table class="data-table">
        <thead>
            <tr>
                <th>Time (s)</th>
                <th>Height (m)</th>
                <th>Speed (m/s)</th>
                <th>Accel (m/s²)</th>
                <th>Fg∥ (N)</th>
                <th>Fric (N)</th>
                <th>Drag (N)</th>
                <th>PE (J)</th>
                <th>KE (J)</th>
                <th>TE (J)</th>
                <th>Fric Loss (J)</th>
                <th>Drag Loss (J)</th>
                <th>H.Speed (m/s)</th>
                <th>V.Speed (m/s)</th>
            </tr>
        </thead>
        <tbody>
    """
    
    # Add data rows
    for i in range(len(times)):
        table_html += f"""
            <tr>
                <td>{times[i]:.1f}</td>
                <td>{heights[i]:.2f}</td>
                <td>{speeds[i]:.2f}</td>
                <td>{accelerations[i]:.2f}</td>
                <td>{forces_g[i]:.2f}</td>
                <td>{forces_f[i]:.2f}</td>
                <td>{forces_d[i]:.2f}</td>
                <td>{energies_pe[i]:.2f}</td>
                <td>{energies_ke[i]:.2f}</td>
                <td>{energies_te[i]:.2f}</td>
                <td>{friction_losses[i]:.2f}</td>
                <td>{drag_losses[i]:.2f}</td>
                <td>{h_speeds[i]:.2f}</td>
                <td>{v_speeds[i]:.2f}</td>
            </tr>
        """
    
    table_html += """
        </tbody>
    </table>
    """
    
    return table_html
    
# Call Avatar
add_avatar_popup()


# ----------------- MAIN SIMULATION LOOP -----------------------------------------------------------
# This loop continuously updates the physics calculations and visual elements

while True:
    rate(100)  # Limit updates to 100 frames per second for stability
    
    # Skip physics calculations if simulation is paused
    if not running:
        continue
    # --- Calculate all forces acting on the sphere ---
    
    # Buoyant force and effective gravity reduction
    F_buoy = rho_air * volume * g            # Buoyant force = density of fluid * volume * gravity
    g_eff  = g * (1 - rho_air / rho_sphere)  # Effective gravity accounting for buoyancy

    # Gravity component along the slope (parallel to the incline)
    Fg_par = mass * g_eff * sin(angle_rad)  # F = m*g*sin(θ)

    # Normal force and dry friction
    # Normal force is perpendicular to the surface and creates friction against motion
    N      = mass * g_eff * cos(angle_rad)   # Normal force = m*g*cos(θ) 
    F_fric = mu_sa * N if angle < 90 else 0  # Friction = μ*N (zero if vertical drop)

    # Air drag opposing motion
    # Air resistance is proportional to velocity squared and opposes motion
    F_drag = 0.5 * rho_air * Cd_sphere * area_cross * speed**2  # F = ½·ρ·C·A·v²
    
    # Calculate energy lost to drag in this time step
    # Energy lost = Force * distance, approximately Force * speed * time step
    drag_loss += F_drag * speed * dt
    
    # Work lost to friction in this time step = F_fric * distance traveled
    friction_loss += F_fric * speed * dt

    # --- Calculate net force and resulting motion ---
    
    # Net force and resulting acceleration along the incline
    F_net       = Fg_par - F_fric - F_drag  # Sum of all forces (positive = downhill)
    acceleration = F_net / mass  # Newton's Second Law: a = F/m

    # Update speed and displacement using numerical integration
    # v = v₀ + a*dt
    speed += acceleration * dt
    if speed < 0:
        speed = 0               # Prevent reversing direction (clamp to zero)
        
    # s = s₀ + v*dt 
    s += speed * dt             # Advance position along the rail
    
    # Update ball position based on displacement 
    # Move the ball along the rail until it reaches the end
    if s <= rail_length:
        disp_vec = rail.axis.norm() * s
        ball.pos  = rail_start + disp_vec + vector(0, show_radius, 0)
        t        += dt
        elapsed_time = t
    else:
        ball.pos         = rail_end + vector(0, show_radius, 0)
        running          = False
        play_button.color = color.blue
        play_button.text  = "Play"
    
    # --- Force final data record at the end of the rail ---
        # Always add a final row with a unique time
        final_time = round(elapsed_time + dt, 2)
        if len(times) == 0 or times[-1] < final_time:
            times.append(final_time)
            heights.append(0.00)  # Final height is zero at the end
            speeds.append(round(speed, 2))
            gravities.append(g)
            forces_g.append(round(Fg_par, 2))
            forces_f.append(round(F_fric, 2))
            forces_d.append(round(F_drag, 2))
            accelerations.append(round(acceleration, 2))
            energies_pe.append(0.00)
            energies_ke.append(round(0.5 * mass * speed**2, 2))
            energies_te.append(round(0.5 * mass * speed**2, 2))
            friction_losses.append(round(friction_loss, 2))
            drag_losses.append(round(drag_loss, 2))
            h_speeds.append(round(speed * cos(angle_rad), 2))
            v_speeds.append(round(speed * sin(angle_rad), 2))
            data_count_label.text = f"Data points: {len(times)}"

    # --- Update UI displays --- 
    
    # Update basic time and speed labels
    time_label.text  = f"Time: {elapsed_time:.2f} s"
    speed_label.text = f"Speed: {speed:.2f} m/s"

    # Compute current height of ball above ground
    height = max(rail_length - s, 0) * sin(angle_rad)

    # --- Energy calculations ---
    
    # Calculate potential, kinetic, and total energy
    PE = mass * g * height  # Potential energy = m*g*h
    KE = 0.5 * mass * speed**2  # Kinetic energy = ½*m*v²
    TE = PE + KE  # Total energy = PE + KE

    # Compute horizontal and vertical velocity components
    H_speed = speed * cos(angle_rad)  # Horizontal component: v*cos(θ)
    V_speed = speed * sin(angle_rad)  # Vertical component: v*sin(θ)

    # Update the energy display with all current values
    energy_label.text = f"Fg∥:{Fg_par:.2f} N   Fric:{F_fric:.2f} N   Drag:{F_drag:.2f} N   a:{acceleration:.2f} m/s²\nPE:{PE:.2f} J   KE:{KE:.2f} J  Fric Loss:{friction_loss:.2f} J  Drag Loss:{drag_loss:.2f} J\n  TE:{TE:.2f} J\nH. Speed:{H_speed:.2f} m/s   V. Speed:{V_speed:.2f} m/s"

    # Record data at regular intervals (every 0.1s)
    if elapsed_time - last_record_time >= 0.1:
        # Store time and measurement data
        times.append(round(elapsed_time, 1))
        heights.append(round(height, 2))
        speeds.append(round(speed, 2))
        gravities.append(g)
        
        # Store all other data
        forces_g.append(round(Fg_par, 2))
        forces_f.append(round(F_fric, 2))
        forces_d.append(round(F_drag, 2))
        accelerations.append(round(acceleration, 2))
        energies_pe.append(round(PE, 2))
        energies_ke.append(round(KE, 2))
        energies_te.append(round(TE, 2))
        friction_losses.append(round(friction_loss, 2))
        drag_losses.append(round(drag_loss, 2))
        h_speeds.append(round(H_speed, 2))
        v_speeds.append(round(V_speed, 2))
        
        # Update data point count
        data_count_label.text = f"Data points: {len(times)}"
        
        # Update the last record time
        last_record_time = elapsed_time
       