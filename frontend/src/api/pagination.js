export function normalizeList(response) {
  return response?.results ?? response ?? [];
}

export async function fetchAllPages(fetcher, params = {}) {
  const items = [];
  let page = 1;
  let response;

  do {
    response = await fetcher({ ...params, page, page_size: 100 });
    items.push(...normalizeList(response));
    page += 1;
  } while (response?.next);

  return items;
}
