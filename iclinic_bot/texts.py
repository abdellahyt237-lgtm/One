from __future__ import annotations

START_ADMIN = (
    "admin..\n\n"
    "Choisissez une option:\n"
    "- ➕ Ajouter matière\n"
    "- 🩺 Ajouter cas ou question\n"
    "- 📥 Demandes d'accès\n"
    "- 🗑️ Supprimer\n"
    "- ↩️ Aller à l'interface utilisateur\n"
)

START_USER = (
    "Bienvenue à iClinic!\n"
    "Demandez l'accès pour utiliser le bot."
)

ACCESS_PENDING = (
    "Votre demande a été envoyée. Merci d'attendre l'approbation de l'admin."
)

ACCESS_GRANTED = "Votre accès a été approuvé."
ACCESS_DENIED = "Votre accès n'est pas encore approuvé."

PROMPT_SUBJECT_NAME = "Entrez le nom de la matière:"
ADDED_SUBJECT = "Matière enregistrée."
PROMPT_CONTENT_TYPE = "Choisissez: cas clinique ou question?"
PROMPT_CASE_TEXT = "Envoyez le texte du cas clinique pour la matière sélectionnée."
PROMPT_QUESTION_TEXT = "Envoyez la question pour la matière sélectionnée."
SAVED_OK = "Enregistré."

NO_DATA = "Aucune donnée."
