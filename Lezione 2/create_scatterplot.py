import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Carica il dataset
# Assicurati che il file 'synthetic_clinic.csv' si trovi nella stessa directory dello script
# o fornisci il percorso completo.
df = pd.read_csv('synthetic_clinic.csv')

# Crea una figura e un asse per il plot
fig, ax = plt.subplots(figsize=(12, 8))

# Definisci i colori per gli eventi CV
colors = {0: 'blue', 1: 'red'}
labels = {0: 'Nessun Evento CV', 1: 'Evento CV'}

# Crea lo scatter plot
scatter = ax.scatter(df['age'], df['ldl'], c=df['cv_event'].map(colors), alpha=0.7, edgecolors='w', s=80)

# Aggiungi etichette e titolo
ax.set_xlabel('Età', fontsize=12)
ax.set_ylabel('Livello LDL', fontsize=12)
ax.set_title('Età vs. Livello LDL per Evento Cardiovascolare', fontsize=16)
ax.grid(True, which='both', linestyle='--', linewidth=0.5)

# Annota i pazienti con età > 80 anni
for index, row in df.iterrows():
    if row['age'] > 80:
        ax.text(row['age'] + 0.5, row['ldl'], f"ID: {int(row['patient_id'])}", fontsize=9, ha='left')

# Crea una legenda personalizzata
from matplotlib.lines import Line2D
legend_elements = [Line2D([0], [0], marker='o', color='w', label=labels[key],
                          markerfacecolor=value, markersize=10) for key, value in colors.items()]
ax.legend(handles=legend_elements, title="Stato Evento CV")


# Mostra il grafico
plt.tight_layout()
plt.show() 