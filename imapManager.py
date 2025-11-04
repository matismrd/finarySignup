# imapManager.py
import imaplib
import email
import re
from email.header import decode_header
from typing import Optional

IMAP_HOST = "imap.gmail.com"

def _decode_bytes(b: bytes) -> str:
    """Décodage sûr d'un payload bytes -> str."""
    if not b:
        return ""
    for enc in ("utf-8", "latin-1", "iso-8859-1"):
        try:
            return b.decode(enc)
        except Exception:
            pass
    return b.decode("utf-8", errors="ignore")

def _extract_code_from_text(text: str, length: int = 6) -> Optional[str]:
    """Retourne le premier match de code numérique de `length` chiffres."""
    if not text:
        return None
    m = re.search(rf"\b\d{{{length}}}\b", text)
    return m.group(0) if m else None

def get_finary_code(
    gmail_user: str,
    gmail_app_password: str,
    from_addr: str = "no-reply@email.finary.com",
    to_addr: Optional[str] = None,
    unread_only: bool = True,
    code_length: int = 6,
    mailbox: str = "INBOX",
    max_messages_to_check: int = 200
) -> Optional[str]:
    """
    Cherche et retourne le code de vérification Finary (ex: 808096).
    Filtrage par FROM et TO (utile pour dot-trick).
    Renvoie la chaîne du code (ex: "808096") ou None.
    """

    # Connexion
    mail = imaplib.IMAP4_SSL(IMAP_HOST)
    mail.login(gmail_user, gmail_app_password)
    mail.select(mailbox)

    # Construire la recherche IMAP en arguments séparés (évite les problèmes d'encodage)
    criteria = []
    if unread_only:
        criteria.append("UNSEEN")
    if from_addr:
        criteria.extend(["FROM", from_addr])
    if to_addr:
        criteria.extend(["TO", to_addr])

    # Si aucun critère (rare), utiliser ALL
    if not criteria:
        criteria = ["ALL"]

    # imaplib.search accepte plusieurs arguments séparés
    try:
        status, data = mail.search(None, *criteria)
    except UnicodeEncodeError:
        # En cas de caractères non-ascii dans criteria, retomber sur une version simplifiée
        status, data = mail.search(None, "ALL")

    if status != "OK":
        mail.logout()
        return None

    msg_ids = data[0].split()
    if not msg_ids:
        mail.logout()
        return None

    # On parcourt du plus récent au plus ancien (limité par max_messages_to_check)
    checked = 0
    for msg_id in reversed(msg_ids):
        if checked >= max_messages_to_check:
            break
        checked += 1

        status, msg_data = mail.fetch(msg_id, "(RFC822)")
        if status != "OK" or not msg_data or not msg_data[0]:
            continue

        raw = msg_data[0][1]
        try:
            msg = email.message_from_bytes(raw)
        except Exception:
            continue

        # 1) Cherche dans le sujet (souvent le code y est)
        subj = msg.get("Subject", "")
        try:
            dh = decode_header(subj)
            decoded_subject = " ".join(
                (tok[0].decode(tok[1] or "utf-8") if isinstance(tok[0], bytes) else str(tok[0]))
                for tok in dh
            )
        except Exception:
            decoded_subject = subj or ""

        code = _extract_code_from_text(decoded_subject, length=code_length)
        if code:
            mail.logout()
            return code

        # 2) Cherche dans le corps (texte / html)
        body_text = ""
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                disp = str(part.get("Content-Disposition") or "")
                if ctype in ("text/plain", "text/html") and "attachment" not in disp:
                    payload = part.get_payload(decode=True)
                    if payload:
                        part_text = _decode_bytes(payload)
                        if ctype == "text/html":
                            # Enlever balises HTML de façon simple
                            part_text = re.sub(r"<[^>]+>", " ", part_text)
                        body_text += "\n" + part_text
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body_text = _decode_bytes(payload)

        # Aussi vérifier l'en-tête "To" (utile si le serveur a modifié les headers)
        to_header = msg.get("To", "") or msg.get("Delivered-To", "")
        search_space = decoded_subject + "\n" + to_header + "\n" + body_text

        code = _extract_code_from_text(search_space, length=code_length)
        if code:
            mail.logout()
            return code

    mail.logout()
    return None
