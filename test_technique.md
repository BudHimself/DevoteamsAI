# Test Technique — Optimisation de l'Infrastructure Technique

## Contexte

Ce test technique consiste à développer une **application modulaire** répondant à une problématique concrète pour une PME française : l'optimisation de l'infrastructure technique.

La solution doit être structurée en **plusieurs étapes (nœuds)** qui se succèdent pour transformer et enrichir les données progressivement.

> Vous êtes libre de choisir le langage, le framework, les outils (LangGraph, LangChain, etc.) ainsi que le modèle de LLM (OpenAI, Mistral, Claude, etc.).

---

## Objectif Principal

Développer un pipeline modulaire capable de :

1. **Ingérer et analyser** des données techniques simulées (fichier JSON ou flux temps réel)
2. **Détecter des anomalies** sur les indicateurs clés (CPU, latence, mémoire, etc.)
3. **Générer des recommandations** concrètes sous forme de rapport structuré (JSON ou console)

---

## Fonctionnalités Attendues

### 1. Ingestion et Analyse de Données Techniques
- Lire des données issues d'un fichier JSON ou d'un flux en temps réel
- Parser et normaliser les métriques pour les rendre exploitables par les étapes suivantes

### 2. Détection d'Anomalies
- Identifier les indicateurs qui dépassent des seuils critiques, par exemple :
  - Utilisation CPU excessive (ex. > 80%)
  - Latence réseau élevée (ex. > 200 ms)
  - Usage mémoire ou disque critique
  - Services en état dégradé ou hors ligne
  - Taux d'erreur anormal

### 3. Génération de Recommandations
- Produire un rapport structuré proposant des **actions concrètes**, par exemple :
  - Répartition de charge (load balancing)
  - Ajustement des ressources allouées
  - Redémarrage ou investigation de services dégradés
  - Optimisation des connexions actives ou des threads

---

## Format d'Entrée

Les données d'entrée sont au format JSON et contiennent les champs suivants :

```json
{
  "timestamp": "2023-10-01T12:00:00Z",
  "cpu_usage": 85,
  "memory_usage": 70,
  "latency_ms": 250,
  "disk_usage": 65,
  "network_in_kbps": 1200,
  "network_out_kbps": 900,
  "io_wait": 5,
  "thread_count": 150,
  "active_connections": 45,
  "error_rate": 0.02,
  "uptime_seconds": 360000,
  "temperature_celsius": 65,
  "power_consumption_watts": 250,
  "service_status": {
    "database": "online",
    "api_gateway": "degraded",
    "cache": "online"
  }
}
```

### Description des Champs

| Champ | Type | Description |
|---|---|---|
| `timestamp` | string (ISO 8601) | Horodatage de la mesure |
| `cpu_usage` | integer (%) | Pourcentage d'utilisation du CPU |
| `memory_usage` | integer (%) | Pourcentage d'utilisation de la mémoire RAM |
| `latency_ms` | integer (ms) | Latence réseau en millisecondes |
| `disk_usage` | integer (%) | Pourcentage d'utilisation du disque |
| `network_in_kbps` | integer (kbps) | Débit entrant réseau |
| `network_out_kbps` | integer (kbps) | Débit sortant réseau |
| `io_wait` | integer (%) | Temps d'attente I/O du CPU |
| `thread_count` | integer | Nombre de threads actifs |
| `active_connections` | integer | Nombre de connexions actives |
| `error_rate` | float | Taux d'erreur (ex. 0.02 = 2%) |
| `uptime_seconds` | integer (s) | Temps de fonctionnement depuis le dernier redémarrage |
| `temperature_celsius` | integer (°C) | Température du système |
| `power_consumption_watts` | integer (W) | Consommation électrique |
| `service_status` | object | État des services critiques (`online` / `degraded` / `offline`) |

---

## Architecture Multi-Nœuds

La solution doit être organisée en **étapes distinctes et chaînées**. Voici un exemple d'architecture recommandée :

```
[Ingestion] → [Analyse & Détection d'Anomalies] → [Génération de Recommandations] → [Rapport Final]
```

Chaque nœud a une responsabilité unique et transmet ses résultats au nœud suivant.

---

## Format de Sortie Attendu

Le rapport final doit être **structuré** (JSON ou affichage console) et inclure :

- La liste des anomalies détectées avec leur niveau de criticité
- Les recommandations associées à chaque anomalie
- Un résumé global de l'état de l'infrastructure

---

## Exigences Techniques

- **Architecture modulaire** : chaque étape du pipeline est indépendante et réutilisable
- **Documentation** : les choix techniques et architecturaux doivent être expliqués via des commentaires dans le code ou un document annexe
- **Liberté technologique** : choix du langage, des bibliothèques et du modèle LLM laissé à la discrétion du développeur

---

## Conseils & Bonnes Pratiques

- Définir des **seuils d'alerte clairs** pour chaque métrique
- Prévoir une gestion des **services dégradés** dans `service_status`
- Structurer les recommandations de façon **actionnable et priorisée**
- Commenter les choix d'architecture pour faciliter la revue de code
