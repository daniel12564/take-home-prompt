import { useLocations } from '../../api/accounts';

interface LocationSelectorProps {
  accountId: string | null;
  value: string | null;
  onChange: (location: string) => void;
}

export function LocationSelector({ accountId, value, onChange }: LocationSelectorProps) {
  const { data, error, isPending } = useLocations(accountId);
  const locations = data ?? [];
  const loading = accountId !== null && isPending;

  let hint: string | null = null;
  if (accountId === null) {
    hint = 'Choose an account first.';
  } else if (data && locations.length === 0) {
    hint = 'This account has no locations yet.';
  }

  return (
    <div className='flex flex-col gap-1'>
      <label htmlFor='location-select' className='text-xs font-medium text-slate-600'>
        Location
      </label>
      <select
        id='location-select'
        value={value !== null && locations.includes(value) ? value : ''}
        disabled={loading || Boolean(error) || locations.length === 0}
        aria-describedby={hint ? 'location-hint' : undefined}
        onChange={(event) => onChange(event.target.value)}
        className='rounded-md border border-slate-300 bg-white px-2 py-1.5 text-sm disabled:bg-slate-100 disabled:text-slate-500'
      >
        <option value=''>{loading ? 'Loading locations…' : 'All locations'}</option>
        {locations.map((location) => (
          <option key={location} value={location}>
            {location}
          </option>
        ))}
      </select>
      {hint && (
        <p id='location-hint' className='text-xs text-slate-500'>
          {hint}
        </p>
      )}
      {error && (
        <p role='alert' className='text-xs text-red-700'>
          {error.message}
        </p>
      )}
    </div>
  );
}
