! SPDX-License-Identifier: MIT
! Original Capsule-Maker client of the separately installed PSolver public API.
program capsule_periodic
  use dictionaries, only: dictionary, dict_init, dict_free, set, operator(//)
  use wrapper_MPI, only: mpiinit, mpifinalize
  use at_domain, only: domain, domain_new, geocode_to_bc_enum, ATOMIC_UNITS
  use Poisson_Solver, only: coulomb_operator, pkernel_init, pkernel_set, &
       pkernel_free, H_potential, dp, gp
  implicit none
  external :: f_lib_initialize, f_lib_finalize
  type(coulomb_operator) :: kernel
  type(domain) :: space
  type(dictionary), pointer :: options
  real(dp), allocatable :: field(:,:,:)
  real(dp) :: ignored(1)
  real(gp) :: energy, length, spacing(3)
  integer :: n, i, j, k, unit, status
  character(len=1024) :: argument, input_file, potential_file, energy_file

  if (command_argument_count() /= 4) error stop 'Expected n density potential energy'
  call get_command_argument(1, argument)
  read(argument, *, iostat=status) n
  if (status /= 0 .or. n < 16 .or. mod(n, 8) /= 0) error stop 'n must be a positive multiple of 8'
  call get_command_argument(2, input_file)
  call get_command_argument(3, potential_file)
  call get_command_argument(4, energy_file)
  length = 2.0_gp * acos(-1.0_gp)
  spacing = length / real(n, gp)
  allocate(field(n,n,n))
  open(newunit=unit, file=trim(input_file), status='old', action='read')
  do k = 1, n
    do j = 1, n
      do i = 1, n
        read(unit, *, iostat=status) field(i,j,k)
        if (status /= 0) error stop 'Incomplete density file'
      end do
    end do
  end do
  close(unit)

  call f_lib_initialize()
  call mpiinit()
  call dict_init(options)
  call set(options//'kernel'//'isf_order', 16)
  call set(options//'kernel'//'screening', 0.0_gp)
  call set(options//'setup'//'accel', 'none')
  space = domain_new(units=ATOMIC_UNITS, bc=geocode_to_bc_enum('P'), &
       acell=[length, length, length])
  kernel = pkernel_init(0, 1, options, space, [n,n,n], spacing)
  call dict_free(options)
  call pkernel_set(kernel, verbose=.false.)
  ignored = 0.0_dp
  ! The density array is overwritten with the potential; pot_ion is ignored.
  call H_potential('G', kernel, field, ignored, energy, 0.0_dp, .false., quiet='yes')
  open(newunit=unit, file=trim(potential_file), status='new', action='write')
  do k = 1, n
    do j = 1, n
      do i = 1, n
        write(unit, '(es26.17e3)') field(i,j,k)
      end do
    end do
  end do
  close(unit)
  open(newunit=unit, file=trim(energy_file), status='new', action='write')
  write(unit, '(es26.17e3)') energy
  close(unit)
  call pkernel_free(kernel)
  call mpifinalize()
  call f_lib_finalize()
  deallocate(field)
end program capsule_periodic
