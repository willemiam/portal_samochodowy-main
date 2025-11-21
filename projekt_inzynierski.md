# Projekt Inżynierski

## Temat Projektu

**Wykorzystanie LLM do kompresji, dekompresji i uatrakcyjniania opisów aukcji samochodowych.**

---

## Plan Badania

### Cel
Porównanie wydajności różnych modeli językowych (LLM) w tworzeniu i modyfikacji opisów.

### Dane
- Pobrać **100 rzeczywistych opisów** z platformy **Otomoto**

### Metodologia

1. **Ekstrakcja kluczowych danych** z oryginalnych opisów
2. **Generowanie nowych treści** przez LLM (testowanie "kompresji" i "dekompresji" tekstu)
3. **Porównanie wytworów AI** z oryginałami

---

## Kwestie Techniczne

### Interfejs
- Całość w **jednym frontendzie**

### Technologia
- **MCP** (Model Context Protocol)
- **RAG** (Retrieval-Augmented Generation)

### Do Sprawdzenia
> **Test A/B**: Czy zastosowanie MCP i RAG faktycznie polepsza wyniki?