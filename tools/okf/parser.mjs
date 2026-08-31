/**
 * Lightweight zero-dependency YAML Frontmatter + Markdown Parser for OKF v0.2.
 */

export function parseYaml(yamlStr) {
  const lines = yamlStr.split(/\r?\n/);
  const root = {};
  const stack = [{ indent: -1, obj: root, key: null, isArr: false }];

  for (let i = 0; i < lines.length; i++) {
    const rawLine = lines[i];
    // Remove comments
    const lineWithoutComment = rawLine.replace(/(^|\s)#.*$/, '');
    if (!lineWithoutComment.trim()) continue;

    const indent = rawLine.search(/\S/);
    const line = lineWithoutComment.trim();

    while (stack.length > 1 && indent <= stack[stack.length - 1].indent) {
      stack.pop();
    }

    const current = stack[stack.length - 1];

    // Array item: - ...
    if (line.startsWith('-')) {
      const itemContent = line.slice(1).trim();
      let parentArr;

      if (Array.isArray(current.obj)) {
        parentArr = current.obj;
      } else if (current.key && Array.isArray(current.obj[current.key])) {
        parentArr = current.obj[current.key];
      } else if (current.key && current.obj[current.key] === undefined) {
        current.obj[current.key] = [];
        parentArr = current.obj[current.key];
      }

      if (!parentArr) continue;

      if (itemContent.includes(':')) {
        // Object item in array, e.g. - name: NCERT
        const colonIdx = itemContent.indexOf(':');
        const k = itemContent.slice(0, colonIdx).trim();
        const v = parseValue(itemContent.slice(colonIdx + 1).trim());
        const newObj = { [k]: v };
        parentArr.push(newObj);
        stack.push({ indent, obj: newObj, key: k, isArr: false });
      } else if (itemContent.length > 0) {
        // Scalar item in array, e.g. - magnesium-ribbon
        parentArr.push(parseValue(itemContent));
      } else {
        // Empty array item, next lines will define an object
        const newObj = {};
        parentArr.push(newObj);
        stack.push({ indent, obj: newObj, key: null, isArr: false });
      }
      continue;
    }

    // Key-value pair: key: value
    const colonIdx = line.indexOf(':');
    if (colonIdx !== -1) {
      const key = line.slice(0, colonIdx).trim();
      const rest = line.slice(colonIdx + 1).trim();

      if (rest === '') {
        // Could be start of object or array
        current.obj[key] = undefined;
        current.key = key;
        stack.push({ indent, obj: current.obj, key, isArr: false });
      } else if (rest.startsWith('[') && rest.endsWith(']')) {
        // Inline array: [a, b, c]
        const items = rest
          .slice(1, -1)
          .split(',')
          .map((s) => parseValue(s.trim()))
          .filter((s) => s !== '');
        current.obj[key] = items;
      } else {
        current.obj[key] = parseValue(rest);
      }
    }
  }

  return root;
}

function parseValue(val) {
  if (val === '' || val === null || val === undefined) return '';
  // Quoted string
  if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
    return val.slice(1, -1);
  }
  if (val === 'true') return true;
  if (val === 'false') return false;
  if (val === 'null') return null;
  if (!isNaN(Number(val)) && val !== '') return Number(val);
  return val;
}

export function parseOkfDocument(content) {
  const match = content.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/);
  if (!match) {
    return { frontmatter: {}, body: content.trim() };
  }
  const frontmatterStr = match[1];
  const body = match[2].trim();
  const frontmatter = parseYaml(frontmatterStr);
  return { frontmatter, body };
}
