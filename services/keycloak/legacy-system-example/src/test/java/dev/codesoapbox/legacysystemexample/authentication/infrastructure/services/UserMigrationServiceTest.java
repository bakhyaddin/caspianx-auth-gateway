package dev.codesoapbox.legacysystemexample.authentication.infrastructure.services;

import dev.codesoapbox.legacysystemexample.authentication.domain.model.UserMigrationDetails;
import dev.codesoapbox.legacysystemexample.authentication.domain.model.TestUserDataProvider;
import dev.codesoapbox.legacysystemexample.authentication.domain.model.User;
import dev.codesoapbox.legacysystemexample.authentication.domain.repositories.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class UserMigrationServiceTest {

    @Mock
    private UserRepository userRepository;

    private UserMigrationService migrationService;
    private TestUserDataProvider userDataProvider;

    @BeforeEach
    void setUp() {
        migrationService = new UserMigrationService(userRepository);
        userDataProvider = new TestUserDataProvider();
    }

    @Test
    void shouldGetMigrationDetailsByUsername() {
        User user = userDataProvider.full();
        String username = user.getUsername();

        when(userRepository.findByUsername(username))
                .thenReturn(Optional.of(user));

        Optional<UserMigrationDetails> details = migrationService.getMigrationDetails(username);

        assertTrue(details.isPresent());
        assertEquals(username, details.get().getUsername());
        assertTrue(details.get().isEmailVerified());
    }

    @Test
    void shouldGetMigrationDetailsByEmail() {
        User user = userDataProvider.full();
        String email = user.getEmail();

        when(userRepository.findByEmail(email))
                .thenReturn(Optional.of(user));

        Optional<UserMigrationDetails> details = migrationService.getMigrationDetails(email);

        assertTrue(details.isPresent());
        assertEquals(email, details.get().getEmail());
        assertTrue(details.get().isEmailVerified());
    }

    @Test
    void shouldReturnEmptyOptionalWhenNonExistentUsernameAndEmail() {
        when(userRepository.findByUsername("non_existent"))
                .thenReturn(Optional.empty());
        when(userRepository.findByEmail("non_existent"))
                .thenReturn(Optional.empty());

        Optional<UserMigrationDetails> details = migrationService.getMigrationDetails("non_existent");

        assertFalse(details.isPresent());
    }

    @Test
    void shouldVerifyCorrectPasswordForUsername() {
        User user = userDataProvider.full();
        String username = user.getUsername();

        when(userRepository.findByUsername(username))
                .thenReturn(Optional.of(user));

        boolean verified = migrationService.passwordIsCorrect(username, user.getPassword());

        assertTrue(verified);
    }

    @Test
    void shouldVerifyCorrectPasswordForEmail() {
        User user = userDataProvider.full();
        String email = user.getEmail();

        when(userRepository.findByEmail(email))
                .thenReturn(Optional.of(user));

        boolean verified = migrationService.passwordIsCorrect(email, user.getPassword());

        assertTrue(verified);
    }

    @Test
    void shouldVerifyIncorrectPassword() {
        User user = userDataProvider.full();
        String username = user.getUsername();

        when(userRepository.findByUsername(username))
                .thenReturn(Optional.of(user));

        boolean verified = migrationService.passwordIsCorrect(username, "wrong_password");

        assertFalse(verified);
    }
}