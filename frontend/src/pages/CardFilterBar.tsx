import * as React from 'react';
import { Box, FormControl, InputLabel, Select, MenuItem, Checkbox, ListItemText, OutlinedInput, Grid } from '@mui/material';
import type { SelectChangeEvent } from '@mui/material';

const setOptions = [
  'EB01', 'EB02', 'OP01', 'OP02', 'OP03', 'OP04', 'OP05', 'OP06', 'OP07', 'OP08', 'OP09', 'OP10', 'OP11', 'OP12',
  'P', 'PRB01', 'ST01', 'ST02', 'ST03', 'ST04', 'ST05', 'ST06', 'ST07', 'ST08', 'ST09', 'ST10', 'ST11', 'ST12', 'ST13', 'ST14', 'ST15', 'ST16', 'ST17', 'ST18', 'ST19', 'ST20', 'ST21', 'ST22', 'ST23', 'ST24', 'ST25', 'ST26', 'ST27', 'ST28'
];
const typeOptions = ['LEADER', 'CHARACTER', 'EVENT', 'STAGE'];
const colorOptions = ['Red', 'Green', 'Purple', 'Blue', 'Black', 'Yellow'];
const costOptions = ['-', 1,2,3,4,5,6,7,8,9,10];
const powerOptions = [0,1000,2000,3000,4000,5000,6000,7000,8000,9000,10000,11000,12000,13000];
const counterOptions = [0,1000,2000];
const rarityOptions = ['L','C','UC','R','SR','SEC','P'];

export type FilterState = {
  set: string[];
  type: string[];
  color: string[];
  cost: (string | number)[];
  power: number[];
  counter: number[];
  rarity: string[];
};

type MultiSelectProps = {
  label: string;
  options: (string | number)[];
  value: (string | number)[];
  onChange: (event: SelectChangeEvent<(string | number)[]>) => void;
};

function MultiSelect({ label, options, value, onChange }: MultiSelectProps) {
  return (
    <FormControl sx={{ m: 0.5, minWidth: 120, maxWidth: 180 }} size="small">
      <InputLabel>{label}</InputLabel>
      <Select
        multiple
        value={value}
        onChange={onChange}
        input={<OutlinedInput label={label} />}
        renderValue={(selected) => (selected as (string | number)[]).join(', ')}
        MenuProps={{ PaperProps: { style: { maxHeight: 300 } } }}
        sx={{
          backgroundColor: '#fff',
          color: '#222',
          '.MuiOutlinedInput-notchedOutline': { borderColor: '#bbb' },
          '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#888' },
          '&.Mui-focused .MuiOutlinedInput-notchedOutline': { borderColor: '#3578e6' },
        }}
      >
        {options.map((opt) => (
          <MenuItem key={opt} value={opt}>
            <Checkbox checked={value.indexOf(opt) > -1} />
            <ListItemText primary={opt} />
          </MenuItem>
        ))}
      </Select>
    </FormControl>
  );
}

type CardFilterBarProps = {
  filters: FilterState;
  setFilters: React.Dispatch<React.SetStateAction<FilterState>>;
};

const CardFilterBar: React.FC<CardFilterBarProps> = ({ filters, setFilters }) => {
  return (
    <Box sx={{ background: 'transparent', p: 1 }}>
      <Grid container spacing={1}>
        <Grid item>
          <MultiSelect label="Set" options={setOptions} value={filters.set} onChange={(e) => setFilters(f => ({...f, set: e.target.value as string[]}))} />
        </Grid>
        <Grid item>
          <MultiSelect label="Type" options={typeOptions} value={filters.type} onChange={(e) => setFilters(f => ({...f, type: e.target.value as string[]}))} />
        </Grid>
        <Grid item>
          <MultiSelect label="Color" options={colorOptions} value={filters.color} onChange={(e) => setFilters(f => ({...f, color: e.target.value as string[]}))} />
        </Grid>
        <Grid item>
          <MultiSelect label="Cost" options={costOptions} value={filters.cost} onChange={(e) => setFilters(f => ({...f, cost: e.target.value as (string | number)[]}))} />
        </Grid>
        <Grid item>
          <MultiSelect label="Power" options={powerOptions} value={filters.power} onChange={(e) => setFilters(f => ({...f, power: e.target.value as number[]}))} />
        </Grid>
        <Grid item>
          <MultiSelect label="Counter" options={counterOptions} value={filters.counter} onChange={(e) => setFilters(f => ({...f, counter: e.target.value as number[]}))} />
        </Grid>
        <Grid item>
          <MultiSelect label="Rarity" options={rarityOptions} value={filters.rarity} onChange={(e) => setFilters(f => ({...f, rarity: e.target.value as string[]}))} />
        </Grid>
      </Grid>
    </Box>
  );
};

export default CardFilterBar; 