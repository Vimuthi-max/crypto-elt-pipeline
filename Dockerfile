# 1. කුඩා Python Linux Environment එකක් තෝරා ගැනීම
FROM python:3.10-slim

# 2. Container එක ඇතුළේ වැඩ කරන Folder එක සකසා ගැනීම
WORKDIR /app

# 3. Libraries ලැයිස්තුව Container එක ඇතුළට Copy කර ඉන්ස්ටෝල් කිරීම
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. අපේ pipeline.py කෝඩ් එක Container එක ඇතුළට Copy කිරීම
COPY pipeline.py .

# 5. Container එක Run වන විට ක්‍රියාත්මක විය යුතු Command එක
CMD ["python", "pipeline.py"]