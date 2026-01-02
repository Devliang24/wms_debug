import { Card } from 'antd'

type Props = { title: string }

export default function PlaceholderPage({ title }: Props) {
  return <Card title={title}>TODO</Card>
}
