import { useCallback, useEffect, useState } from "react";
import {
  Button,
  Card,
  Form,
  Input,
  InputNumber,
  Modal,
  Popconfirm,
  Space,
  Table,
  Typography,
  message,
} from "antd";
import type { ColumnsType } from "antd/es/table";

import {
  createProduct,
  deleteProduct,
  listProducts,
  updateProduct,
  type Product,
  type ProductInput,
} from "../api/products";

function CrudPage() {
  const [form] = Form.useForm<ProductInput>();
  const [messageApi, contextHolder] = message.useMessage();
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product>();
  const [modalOpen, setModalOpen] = useState(false);

  const fetchProducts = useCallback(async () => {
    setLoading(true);
    try {
      setProducts(await listProducts());
    } catch (error) {
      messageApi.error(getErrorMessage(error));
    } finally {
      setLoading(false);
    }
  }, [messageApi]);

  useEffect(() => {
    void fetchProducts();
  }, [fetchProducts]);

  const openCreateModal = () => {
    setEditingProduct(undefined);
    form.resetFields();
    setModalOpen(true);
  };

  const openEditModal = (product: Product) => {
    setEditingProduct(product);
    form.setFieldsValue({
      name: product.name,
      description: product.description ?? undefined,
      price: Number(product.price),
      stock: product.stock,
    });
    setModalOpen(true);
  };

  const handleSubmit = async () => {
    const values = await form.validateFields();
    setSaving(true);

    try {
      if (editingProduct) {
        await updateProduct(editingProduct.id, values);
        messageApi.success("商品已更新");
      } else {
        await createProduct(values);
        messageApi.success("商品已创建");
      }

      setModalOpen(false);
      await fetchProducts();
    } catch (error) {
      messageApi.error(getErrorMessage(error));
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (product: Product) => {
    try {
      await deleteProduct(product.id);
      messageApi.success("商品已删除");
      await fetchProducts();
    } catch (error) {
      messageApi.error(getErrorMessage(error));
    }
  };

  const columns: ColumnsType<Product> = [
    {
      title: "名称",
      dataIndex: "name",
    },
    {
      title: "描述",
      dataIndex: "description",
      render: (value: string | null) => value || "-",
    },
    {
      title: "价格",
      dataIndex: "price",
      render: (value: string | number) => `¥${Number(value).toFixed(2)}`,
    },
    {
      title: "库存",
      dataIndex: "stock",
    },
    {
      title: "创建时间",
      dataIndex: "created_at",
      render: (value: string) => new Date(value).toLocaleString(),
    },
    {
      title: "操作",
      render: (_, record) => (
        <Space>
          <Button type="link" onClick={() => openEditModal(record)}>
            编辑
          </Button>
          <Popconfirm
            title="确认删除这个商品？"
            okText="删除"
            cancelText="取消"
            onConfirm={() => handleDelete(record)}
          >
            <Button type="link" danger>
              删除
            </Button>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <section className="content-page">
      {contextHolder}
      <Card>
        <Space direction="vertical" size="large" className="full-width">
          <Space direction="vertical" size="small">
            <Typography.Title level={2}>FastAPI + MySQL CRUD</Typography.Title>
            <Typography.Text type="secondary">
              这是传统后端 CRUD 学习页：前端表单调用 FastAPI，后端通过 SQLAlchemy 写入 MySQL。
            </Typography.Text>
          </Space>

          <Button type="primary" onClick={openCreateModal}>
            新增商品
          </Button>

          <Table
            rowKey="id"
            columns={columns}
            dataSource={products}
            loading={loading}
            pagination={{ pageSize: 8 }}
          />
        </Space>
      </Card>

      <Modal
        title={editingProduct ? "编辑商品" : "新增商品"}
        open={modalOpen}
        confirmLoading={saving}
        onOk={handleSubmit}
        onCancel={() => setModalOpen(false)}
        okText="保存"
        cancelText="取消"
      >
        <Form form={form} layout="vertical">
          <Form.Item
            label="名称"
            name="name"
            rules={[{ required: true, message: "请输入商品名称" }]}
          >
            <Input placeholder="例如：FastAPI 学习手册" />
          </Form.Item>
          <Form.Item label="描述" name="description">
            <Input.TextArea rows={3} placeholder="可选" />
          </Form.Item>
          <Form.Item
            label="价格"
            name="price"
            rules={[{ required: true, message: "请输入价格" }]}
          >
            <InputNumber min={0.01} precision={2} className="full-width" />
          </Form.Item>
          <Form.Item
            label="库存"
            name="stock"
            rules={[{ required: true, message: "请输入库存" }]}
          >
            <InputNumber min={0} precision={0} className="full-width" />
          </Form.Item>
        </Form>
      </Modal>
    </section>
  );
}

function getErrorMessage(error: unknown): string {
  return error instanceof Error ? error.message : "请求失败";
}

export default CrudPage;
