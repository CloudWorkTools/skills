import { existsSync, readFileSync, readdirSync, realpathSync } from 'node:fs';
import { dirname, isAbsolute, join, relative, resolve, sep } from 'node:path';

function withoutFences(markdown) {
  let fence;
  return markdown.split('\n').map(line => {
    const marker = line.match(/^ {0,3}(`{3,}|~{3,})(.*)$/);
    if (fence) {
      if (marker && marker[1][0] === fence[0] && marker[1].length >= fence.length && !marker[2].trim()) fence = undefined;
      return '';
    }
    if (marker) {
      fence = marker[1];
      return '';
    }
    return line;
  }).join('\n');
}

function anchors(markdown) {
  const result = new Set();
  for (const match of markdown.matchAll(/^ {0,3}#{1,6}\s+(.+?)\s*#*\s*$/gm)) {
    const slug = match[1].toLowerCase().replace(/!?(?:\[([^\]]+)\])\([^)]*\)/g, '$1')
      .replace(/[^\p{L}\p{M}\p{N}_\-\s]/gu, '').replace(/\s/g, '-');
    let id = slug;
    for (let index = 1; result.has(id); index++) id = `${slug}-${index}`;
    result.add(id);
  }
  return result;
}

// Supports the bundled Markdown: ATX headings and single-line inline/reference links.
// HTML/custom IDs, Setext headings and multiline links are outside this small guard.
export function markdownLinkErrors(directory) {
  const root = realpathSync(directory);
  const documents = new Map();
  function collect(path) {
    for (const entry of readdirSync(path, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name, 'en'))) {
      const child = join(path, entry.name);
      if (entry.isDirectory()) collect(child);
      else if (entry.name.endsWith('.md')) documents.set(child, withoutFences(readFileSync(child, 'utf8')));
    }
  }
  collect(root);
  const errors = [];
  const confined = path => {
    const location = relative(root, path);
    return location !== '..' && !location.startsWith(`..${sep}`) && !isAbsolute(location);
  };
  for (const [file, markdown] of documents) {
    const references = new Map();
    const normalize = label => label.trim().replace(/\s+/g, ' ').toLowerCase();
    const content = markdown.replace(/^ {0,3}\[([^\]]+)\]:\s*(?:<([^>]+)>|(\S+)).*$/gm, (_, label, angled, plain) => {
      if (!references.has(normalize(label))) references.set(normalize(label), angled ?? plain);
      return '';
    }).replace(/(`+)[\s\S]*?\1/g, '');
    const links = [];
    const remaining = content.replace(/!?\[([^\]\n]*)\]\(\s*(?:<([^>\n]+)>|([^\s()]*(?:\([^()]*\)[^\s()]*)*))(?:\s+["'][^\n]*?["'])?\s*\)/g, (_, label, angled, plain) => {
      links.push(angled ?? plain);
      return '';
    });
    for (const match of remaining.matchAll(/!?\[([^\]\n]+)\](?:\[([^\]\n]*)\])?/g)) {
      const key = normalize(match[2] || match[1]);
      if (references.has(key)) links.push(references.get(key));
      else if (match[2] !== undefined) errors.push(`${relative(root, file)}: missing reference [${key}]`);
    }
    for (const link of links) {
      if (/^(?:[a-z][a-z\d+.-]*:|\/\/)/i.test(link)) continue;
      const report = reason => errors.push(`${relative(root, file)}: ${link}: ${reason}`);
      let path, fragment;
      try {
        const hash = link.indexOf('#');
        path = decodeURIComponent((hash < 0 ? link : link.slice(0, hash)).split('?')[0]);
        fragment = hash < 0 ? '' : decodeURIComponent(link.slice(hash + 1));
      } catch {
        report('invalid URL encoding');
        continue;
      }
      const target = path ? resolve(dirname(file), path) : file;
      if (!confined(target) || (existsSync(target) && !confined(realpathSync(target)))) {
        report('escapes installed skill');
      } else if (!existsSync(target)) {
        report('missing target');
      } else if (fragment && target.endsWith('.md') && !anchors(documents.get(target) ?? withoutFences(readFileSync(target, 'utf8'))).has(fragment)) {
        report('missing heading anchor');
      }
    }
  }
  return errors;
}
