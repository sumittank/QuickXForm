const normalizeText = (value = "") =>
  value
    .toLowerCase()
    .replace(/[^a-z0-9\s]/g, " ")
    .replace(/\s+/g, " ")
    .trim();

const similarityScore = (left = "", right = "") => {
  const a = normalizeText(left);
  const b = normalizeText(right);
  if (!a || !b) {
    return 0;
  }

  if (a === b) {
    return 1;
  }

  if (a.includes(b) || b.includes(a)) {
    return Math.min(a.length, b.length) / Math.max(a.length, b.length);
  }

  const aTokens = new Set(a.split(" ").filter(Boolean));
  const bTokens = new Set(b.split(" ").filter(Boolean));
  const overlap = [...aTokens].filter((token) => bTokens.has(token)).length;
  const union = new Set([...aTokens, ...bTokens]).size;
  return union ? overlap / union : 0;
};

const minutesBetweenTimes = (left = "", right = "") => {
  if (!left || !right) {
    return null;
  }

  const [leftHour, leftMinute] = left.split(":").map(Number);
  const [rightHour, rightMinute] = right.split(":").map(Number);
  if (
    Number.isNaN(leftHour) ||
    Number.isNaN(leftMinute) ||
    Number.isNaN(rightHour) ||
    Number.isNaN(rightMinute)
  ) {
    return null;
  }

  return Math.abs(leftHour * 60 + leftMinute - (rightHour * 60 + rightMinute));
};

export const detectDuplicateEntry = (entry, savedEntries) => {
  let bestMatch = null;

  for (const savedEntry of savedEntries) {
    const nameScore = similarityScore(entry.hcpName, savedEntry.hcpName);
    const sameDate = Boolean(entry.date && savedEntry.date && entry.date === savedEntry.date);
    const timeGap = minutesBetweenTimes(entry.time, savedEntry.time);
    const closeTime = timeGap !== null && timeGap <= 30;
    const topicScore = similarityScore(entry.topicsDiscussed, savedEntry.topicsDiscussed);

    const isDuplicate = nameScore >= 0.75 && sameDate && (closeTime || topicScore >= 0.4);
    if (!isDuplicate) {
      continue;
    }

    const confidence = Math.min(
      100,
      Math.round(nameScore * 45 + (sameDate ? 25 : 0) + (closeTime ? 20 : 0) + topicScore * 10),
    );

    const reasons = [];
    if (nameScore >= 0.9) {
      reasons.push("doctor name is almost identical");
    } else {
      reasons.push("doctor name is similar");
    }
    reasons.push("interaction date matches");
    if (closeTime) {
      reasons.push("interaction time is close");
    }
    if (topicScore >= 0.4) {
      reasons.push("topics overlap");
    }

    if (!bestMatch || confidence > bestMatch.confidence) {
      bestMatch = {
        is_duplicate: true,
        confidence: Math.max(confidence, 60),
        matched_record: savedEntry,
        reason: reasons.join(", "),
      };
    }
  }

  return bestMatch;
};
