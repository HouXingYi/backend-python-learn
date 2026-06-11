import { API_BASE_URL } from "./config";

export type Product = {
  id: number;
  name: string;
  description?: string | null;
  price: string | number;
  stock: number;
  created_at: string;
};

export type ProductInput = {
  name: string;
  description?: string | null;
  price: number;
  stock: number;
};

type ErrorResponse = {
  detail?: unknown;
};

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });

  if (!response.ok) {
    throw new Error(await getErrorMessage(response));
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

async function getErrorMessage(response: Response): Promise<string> {
  try {
    const data = (await response.json()) as ErrorResponse;
    if (typeof data.detail === "string") {
      return data.detail;
    }
  } catch {
    // Fall back to a status-only message when the backend returns non-JSON.
  }

  return `请求失败：${response.status}`;
}

export function listProducts(): Promise<Product[]> {
  return request<Product[]>("/api/products");
}

export function createProduct(product: ProductInput): Promise<Product> {
  return request<Product>("/api/products", {
    method: "POST",
    body: JSON.stringify(product),
  });
}

export function updateProduct(
  id: number,
  product: Partial<ProductInput>,
): Promise<Product> {
  return request<Product>(`/api/products/${id}`, {
    method: "PUT",
    body: JSON.stringify(product),
  });
}

export function deleteProduct(id: number): Promise<void> {
  return request<void>(`/api/products/${id}`, {
    method: "DELETE",
  });
}
