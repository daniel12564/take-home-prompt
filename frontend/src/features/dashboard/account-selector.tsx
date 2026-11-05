import { useAccounts } from '../../api/accounts';

interface AccountSelectorProps {
  value: string | null;
  onChange: (accountId: string) => void;
}

function describe(name: string, count: number) {
  return `${name} (${count} ${count === 1 ? 'location' : 'locations'})`;
}

export function AccountSelector({ value, onChange }: AccountSelectorProps) {
  const { data, error, isPending } = useAccounts();

  return (
    <div className='flex flex-col gap-1'>
      <label htmlFor='account-select' className='text-xs font-medium text-slate-600'>
        Account
      </label>
      <select
        id='account-select'
        value={value ?? ''}
        disabled={isPending || Boolean(error)}
        onChange={(event) => onChange(event.target.value)}
        className='rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm disabled:bg-slate-100 disabled:text-slate-500'
      >
        <option value=''>{isPending ? 'Loading accounts…' : 'Select an account'}</option>
        {data?.map((account) => (
          <option key={account.id} value={String(account.id)}>
            {describe(account.name, account.location_count)}
          </option>
        ))}
      </select>
      {error && (
        <p role='alert' className='text-xs text-red-700'>
          {error.message}
        </p>
      )}
    </div>
  );
}
