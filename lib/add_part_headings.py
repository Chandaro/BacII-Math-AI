"""Repeat each part's instruction at the start of its answer, as in printed answer books:
  ក. កំណត់បំណែងចែកប្រូបាបនៃ $X$ ៖
  <working>
Terms that appear only in questions are not learned, because training scores answers only.
Usage: heading(question, answer) -> answer."""
import re
KH = re.compile(r"[ក-៿]")
PART = re.compile(r"(?m)^([កខគឃងចឆ])\.\s*(.+?)\s*$")

def strip_math(s):
    return re.sub(r"\$\$?.*?\$\$?", "", s, flags=re.S)

def heading(q, a):
    parts = {k: v for k, v in PART.findall(q)}
    if not parts: return a
    out = []
    for line in a.split("\n"):
        m = re.match(r"^([កខគឃងចឆ])\.\s*(.*)$", line)
        if m and m.group(1) in parts:
            k, rest = m.groups(); instr = parts.pop(k)
            body = re.sub(r"\s*[។?]\s*$", "", instr).strip()
            words = strip_math(body)
            if len(KH.findall(words)) >= 4 and len(body) <= 140 and not rest.startswith(body[:12]):
                out.append(f"{k}. {body} ៖")
                if rest.strip(): out.append(rest.lstrip(" ៖"))
                continue
        out.append(line)
    return "\n".join(out)

if __name__ == "__main__":
    q = "ក. កំណត់បំណែងចែកប្រូបាបនៃ $X$ ។\nខ. គណនា $E(X)$ ។"
    a = "ក. $X$ អាចយកតម្លៃ $0,1$ ។\nP...\nខ. $E(X)=1$"
    print(heading(q, a))
