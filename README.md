<h1 align="center">👋🤖 ¡Hola robot internauta! Soy Remgo</h1>
<h3 align="center">🎓 Estudiante de Ingeniería Electrónica | Universidad Peruana de Ciencias Aplicadas (UPC)</h3>

<p align="center">
  <img src="remgo_walking.gif" width="200" alt="Remgo walking animation"/>
</p>
<p align="center">
Actualmente curso el <b>sexto año</b> de carrera, apasionado por la intersección entre <b>automatización industrial</b>, <b>redes de comunicación</b> e <b>inmótica</b>. Mi enfoque está en desarrollar soluciones robustas y escalables para sistemas embebidos e industriales.
</p>

---

## 🔧 Áreas de Especialización

- **Automatización Industrial**: Diseño y programación de sistemas de control para procesos industriales
- **Programación de PLCs**: Experiencia en **Siemens** (TIA Portal, STEP 7)
- **Redes de Comunicación Industrial**: Profinet, Modbus TCP/IP, OPC UA
<!--- **Domótica y IoT**: Integración de dispositivos inteligentes y protocolos de comunicación (MQTT, KNX)-->
- **Sistemas Embebidos**: [PIC18F57Q43](https://www.microchip.com/en-us/product/pic18f57q43), [PIC18F47Q10](https://www.microchip.com/en-us/product/pic18f47q10)

---

## 💻 Stack Tecnológico

### Lenguajes de Programación
![Python](https://img.shields.io/badge/-Python-3776AB?style=flat-square&logo=python&logoColor=white)
![C](https://img.shields.io/badge/-C-A8B9CC?style=flat-square&logo=c&logoColor=white)
![C++](https://img.shields.io/badge/-C++-00599C?style=flat-square&logo=cplusplus&logoColor=white)
![Ladder Logic](https://img.shields.io/badge/-Ladder_Logic-009999?style=flat-square)

### Herramientas y Plataformas
- **Siemens TIA Portal y STEP 7**: Programación de PLCs S7-1200, configuración de redes Profinet
- **MPLAB X IDE**: Programación de microcontroladores de Microchip

## 📚 Proyectos Destacados

### 📄[ETL-UPC-Syllabus](https://github.com/remgo696/ETL-UPC-Syllabus)
> Pipeline ETL desarrollado en Python 🐍 para conseguir información estructurada desde los sílabos en PDF de la UPC.
- **Librerias principales**: pdfplumber, reportlab, re, json, configparser
- **Enfoque**: Arquitectura escalable y modular, con separación clara entre las fases Extract, Transform y Load.
- **Objetivo:** Estandarizar y limpiar datos académicos (información general, unidades de aprendizaje, evaluaciones) para su posterior análisis o uso en aplicaciones inteligentes.
- **Diseño:** Basado en clases (`Course`, `Unit`, `Exam`, `SyllabusRaw`) que representan la **semántica de negocio** del dominio educativo.

### 📖 [TheAssemblyChronicles-PIC](https://github.com/remgo696/TheAssemblyChronicles-PIC)
> Guía técnica de referencia para microcontroladores PIC18F57Q43 y PIC18F47Q10 en Assembly y C.
- **Stack**: MkDocs, Python, C, Assembly | Desplegado en GitHub Pages con CI/CD vía GitHub Actions ([Link](https://remgo696.github.io/TheAssemblyChronicles-PIC/))
- **Contenido**: Arquitectura del PIC18F, manejo de memoria, interrupciones, periféricos (timers, LCD1602) y proyectos funcionales
- **Enfoque**: Documentación orientada al aprendizaje para estudiantes de Ingeniería Electrónica, Mecatrónica y Biomédica de la UPC
- **Proyectos incluidos**: Termómetro digital, reloj 24H/12H, fading LED, control de intensidad con encoder rotativo

---

## 🔌 Proyectos con PIC18F47Q10

### 🌡️ [PIC18F47Q10-Thermometer-EUSART](https://github.com/remgo696/PIC18F47Q10-Thermometer-EUSART)
> Termómetro digital con sensor DHT22, LCD 16×2 y transmisión serial vía EUSART2.
- Lee temperatura y humedad, permite alternar entre °C y °F mediante interrupción externa (INT0)
- Conversión °C→°F con aritmética entera, sin punto flotante

### ⏰ [PIC18F47Q10-Clock24H12H](https://github.com/remgo696/PIC18F47Q10-Clock24H12H)
> Reloj digital con formato HH:MM:SS:CC, modos 24H/12H y alarma configurable.
- Base de tiempo precisa de 10 ms usando TMR1 + CCP1 en modo comparación con interrupciones de doble prioridad
- Máquina de estados con detección de pulsación larga (2s) y timeout de inactividad (6s)
- Interfaz con 3 botones (UP, MODE, DOWN) mediante IOC y LCD 16×2

### 💡 [PIC18F47Q10-FadingLED](https://github.com/remgo696/PIC18F47Q10-FadingLED)
> Efecto de desvanecimiento/reaparición suave de LED usando PWM por hardware en la Curiosity Nano.
- CCP1 en modo PWM; TMR0 genera interrupciones a ~120 Hz para ajustar brillo gradualmente
- Ciclo completo de fade en ~1.7 segundos

### 🎛️ [PIC18F47Q10-LEDIntensityControl-LCD16x2-KY040](https://github.com/remgo696/PIC18F47Q10-LEDIntensityControl-LCD16x2-KY040)
> Dimmer de LED controlado por encoder rotativo KY-040 con visualización en LCD 16×2.
- PWM3 a 5 kHz con ajuste de intensidad en incrementos de 2%, mostrado en tiempo real en el LCD
- Arquitectura interrupt-driven: TMR0 muestrea el encoder con debounce, el main loop actualiza PWM y display
- Oscilador a 4 MHz, prescaler 1:4 en TMR0 para sampling a ~1.2 kHz

---

## 📊 Estadísticas de GitHub

![GitHub Stats](https://github-profile-summary-cards.vercel.app/api/cards/stats?username=remgo696&theme=tokyonight)

![Top Languages](https://github-profile-summary-cards.vercel.app/api/cards/repos-per-language?username=remgo696&theme=tokyonight)

---

## 🎯 Objetivos Actuales

<!--- 📖 Profundizar en **arquitecturas de sistemas distribuidos** aplicadas a automatización
- 🔧 Certificación en **Siemens TIA Portal** (TIA-PORTAL-PRO-1)-->
- 🌐 Certificación CCNA
- 💾 Ser un data engineer

---

## 📫 Contacto

- 📧 **Email**: [dvladimirdm@hotmail.com](mailto:dvladimirdm@hotmail.com)
- 💼 **LinkedIn**: [linkedin.com/in/david-díaz-malca](https://www.linkedin.com/in/david-d%C3%ADaz-malca/)

