import matplotlib.pyplot as plt
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, confusion_matrix, ConfusionMatrixDisplay,
)


def mostrar_metricas(y_test, y_pred, nombre_modelo):
    """Imprime las metricas principales y devuelve un diccionario con los valores."""
    acc  = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    rec  = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1   = f1_score(y_test, y_pred, average='weighted', zero_division=0)

    print(f'--- {nombre_modelo} ---')
    print(f'  Accuracy  : {acc:.4f}')
    print(f'  Precision : {prec:.4f}')
    print(f'  Recall    : {rec:.4f}')
    print(f'  F1-Score  : {f1:.4f}')

    return {'modelo': nombre_modelo, 'accuracy': acc,
            'precision': prec, 'recall': rec, 'f1': f1}


def graficar_confusion(y_test, y_pred, nombre_modelo, labels=None):
    """Muestra la matriz de confusion del modelo."""
    cm = confusion_matrix(y_test, y_pred)
    fig, ax = plt.subplots(figsize=(6, 5))
    ConfusionMatrixDisplay(cm, display_labels=labels).plot(
        ax=ax, cmap='Blues', colorbar=False
    )
    ax.set_title(f'Matriz de Confusion - {nombre_modelo}')
    plt.tight_layout()
    plt.show()
