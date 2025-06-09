import ContractView from '../../../components/ContractView'

interface ContractPageProps {
  params: {
    id: string
  }
}

export default async function ContractPage({ params }: ContractPageProps) {
  const contractId = parseInt(params.id)

  if (isNaN(contractId)) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Invalid Contract ID</h1>
          <p className="text-gray-600">The contract ID provided is not valid.</p>
        </div>
      </div>
    )
  }

  return <ContractView contractId={contractId} />
}
